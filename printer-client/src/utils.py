import cups,time
import requests,json,asyncio,os
from collections import deque
from dotenv import load_dotenv
load_dotenv()
def list_printers(conn):
    printers = conn.getPrinters()
    return printers




if __name__ == "__main__":
    printers = list_printers()
    for name, attrs in printers.items():
        print("Printer name:", name)
        print("  Description:", attrs.get("printer-info"))
        print("  Location:", attrs.get("printer-location"))
        print("  State:", attrs.get("printer-state"))
        print("  Is Default:", attrs.get("printer-is-default"))
        print("-" * 40)
def get_default_printer(conn):
    return conn.getDefault()



#polling based

def track_print_job(conn,job_id: int, poll_interval: int = 2, timeout: int = 300):
    """
    Track a CUPS print job until completion or failure.

    :param job_id: CUPS job ID returned by printFile()
    :param poll_interval: seconds between status checks
    :param timeout: max time to wait (seconds)
    :return: final job state string
    """
    start_time = time.time()

    while True:
        # Timeout protection
        if time.time() - start_time > timeout:
            return "TIMEOUT"

        try:
            job = conn.getJobAttributes(job_id)
        except cups.IPPError:
            # Job not found (likely auto-purged after completion)
            return "JOB_NOT_FOUND"

        state_code = job.get("job-state")
        state = JOB_STATES.get(state_code, "UNKNOWN")

        print(f"Job {job_id} → {state}")

        # Terminal states
        if state in {"COMPLETED", "CANCELED", "ABORTED"}:
            return state

        time.sleep(poll_interval)


# ipp event subscriptions based:
import cups
import threading
import time

JOB_STATES = {
    3: "PENDING",
    4: "HELD",
    5: "PRINTING",
    6: "STOPPED",
    7: "CANCELED",
    8: "ABORTED",
    9: "COMPLETED",
}
TERMINAL_STATES = {"COMPLETED", "CANCELED", "ABORTED"}

class CupsGlobalJobListener:
    def __init__(self, lease_duration=86400, renew_margin=300):
        """
        Global CUPS listener.
        :param lease_duration: Subscription lifetime in seconds (default 24h)
        :param renew_margin: Seconds before lease expires to renew
        """
        self.lease_duration = lease_duration
        self.renew_margin = renew_margin
        self.conn = cups.Connection()  # connection owned by listener thread
        self.sub_id = None
        self.callbacks = {}  # job_id -> dict of callbacks
        self.lock = threading.Lock()
        self.running = False
        self.created_at = 0

    def _printer_uri(self):
        """Return a printer URI usable for subscriptions."""
        default = self.conn.getDefault()
        if default:
            return f"/printers/{default}"

        printers = self.conn.getPrinters()
        if not printers:
            raise RuntimeError("No printers available for subscription.")

        fallback = next(iter(printers))
        print(f"Default printer not set; subscription using {fallback}")
        return f"/printers/{fallback}"

    def start(self):
        """Start listener in a background thread."""
        self.running = True
        self._create_subscription()
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        """Stop listener and cancel subscription."""
        self.running = False
        if self.sub_id:
            self.conn.cancelSubscription(self.sub_id)

    def watch_job(self, job_id, *, on_finished=None, on_canceled=None, on_aborted=None):
        """
        Register callbacks for a specific job.
        :param job_id: CUPS job ID
        :param on_finished: callable(job_id, state) for COMPLETED
        :param on_canceled: callable(job_id, state) for CANCELED
        :param on_aborted: callable(job_id, state) for ABORTED
        """
        with self.lock:
            self.callbacks[job_id] = {
                "COMPLETED": on_finished,
                "CANCELED": on_canceled,
                "ABORTED": on_aborted
            }

    def _create_subscription(self):
        """Create or renew CUPS subscription."""
        events = [
            "job-completed",
            "job-aborted",
            "job-canceled"
        ]

        # python-cups expects positional args (printer_uri, events, ...), not an attribute dict
        printer_uri = self._printer_uri()
        self.sub_id = self.conn.createSubscription(
            printer_uri,
            events,
            recipient_uri="ippget://localhost/",
            lease_duration=self.lease_duration,
        )
        self.created_at = time.time()
        print(" CUPS subscription created:", self.sub_id)

    def _renew_if_needed(self):
        """Renew subscription if lease is about to expire."""
        if time.time() - self.created_at > (self.lease_duration - self.renew_margin):
            print(" Renewing CUPS subscription")
            self.conn.cancelSubscription(self.sub_id)
            self._create_subscription()

    def _listen(self):
        """Main listener loop (runs in thread)."""
        while self.running:
            self._renew_if_needed()
            try:
                events = self.conn.getNotifications(self.sub_id, timeout=30)
            except cups.IPPError:
                print(" Subscription lost — recreating")
                self._create_subscription()
                continue

            if not events:
                continue

            for event in events:
                job_id = event.get("notify-job-id")
                state_code = event.get("job-state")
                state = JOB_STATES.get(state_code, "UNKNOWN")

                if state in TERMINAL_STATES:
                    # pop the callback dict
                    with self.lock:
                        job_cbs = self.callbacks.pop(job_id, {})
                    if job_cbs:
                        cb = job_cbs.get(state)
                        if cb:
                            try:
                                cb(job_id, state)
                            except Exception as e:
                                print(f"Error in callback for job {job_id}: {e}")
# job_listener = CupsGlobalJobListener()


def listen_for_job_completion(conn,job_id: int):
    events = [
        "job-completed",
        "job-stopped",
        "job-aborted",
        "job-canceled",
    ]

    printer_uri = CupsGlobalJobListener()._printer_uri()
    sub_id = conn.createSubscription(
        printer_uri,
        events,
        recipient_uri="ippget://localhost/",
        lease_duration=3600,
    )

    print(" Subscription ID:", sub_id)

    try:
        while True:
            events = conn.getNotifications(sub_id, timeout=30)
            if not events:
                continue

            for event in events:
                event_job_id = event["notify-job-id"]
                if event_job_id != job_id:
                    continue

                state_code = event["job-state"]
                state = JOB_STATES.get(state_code, "UNKNOWN")

                if state in {"COMPLETED", "CANCELED", "ABORTED"}:
                    # on_job_finished(job_id, state)
                    return
    finally:
        conn.cancelSubscription(sub_id)


def job_finished(job_id, state):
    print(f" Job {job_id} COMPLETED")

def job_canceled(job_id, state):
    print(f"⚠️ Job {job_id} CANCELED")

def job_aborted(job_id, state):
    print(f"❌ Job {job_id} ABORTED")
def is_cups_job_done(job_id: int):
    """
    Check whether a CUPS job is finished.

    :param job_id: CUPS job ID
    :return: (done: bool, state: str)
    """
    conn = cups.Connection()

    try:
        job = conn.getJobAttributes(job_id)
    except cups.IPPError:
        # Job not found → usually means it is already completed and purged
        return True, "JOB_NOT_FOUND"

    state_code = job.get("job-state")
    state = JOB_STATES.get(state_code, "UNKNOWN")

    return state in TERMINAL_STATES, state


CUPS_JOB_STATES = {
    3: "PENDING",
    4: "HELD",
    5: "PRINTING",
    6: "STOPPED",
    7: "CANCELED",
    8: "ABORTED",
    9: "COMPLETED",
}

def get_pending_jobs():
    """
    Returns a list of pending jobs across all printers.
    """
    conn = cups.Connection()
    jobs = conn.getJobs(which_jobs="all")

    pending_jobs = []

    for job_id, job in jobs.items():
        if job.get("job-state") == 3:
            pending_jobs.append({
                "job_id": job_id,
                "printer": job.get("printer-uri-supported"),
                "title": job.get("job-name"),
                "user": job.get("job-originating-user-name"),
            })

    return pending_jobs
# change this function by cups in linux
def print_file(file_id, file, app, ws, specifications={}):
    """
    Print a file and notify via websocket when done.
    Uses asyncio.run_coroutine_threadsafe to send from this sync thread.
    """
    conn = cups.Connection()  # thread-safe connection
    printer = get_default_printer(conn)
    # data structure of specification:
    """
    specifications:
    [
        {'page':'2', copies:n} .... n
    ]
    """
    job_id = conn.printFile(printer, file, f"{file_id}", specifications)

    while True:
        done, state = is_cups_job_done(job_id)
        if done and state=="COMPLETED":
            print(f"Job {job_id} finished with state: {state}")
            app.queue.pop(0)
            os.remove(file)
            msg = json.dumps({
                "event":"queue_update",
                                       "data":{ "queue":app.queue,"printed_file_id":file_id} # file id is integer here
            })
            try:
                future = asyncio.run_coroutine_threadsafe(ws.send(msg), app.loop)
                future.result(timeout=5)  # wait up to 5s for send to complete
                
                return 
            except Exception as e:
                print(f"Failed to send job_finished over ws: {e}")
                return
        time.sleep(1)  # poll interval


"""
What the job title is used for


System print dialogs

Helps identify the print job in the queue

Useful when printing many files with the same filename

dont rely on that purely for tracking of the file

"""


def download_file(server_name,file_name):
    response = requests.get(server_name+"/static-files/"+file_name,stream=True)
    response.raise_for_status()
    try:
        path = os.environ.get("upload_file_path")
        with open(f"{path}{file_name}","wb") as f:
            for chuck in response.iter_content(chunk_size=8192):
                f.write(chuck)
            f.close()
        return 1
    except: 
        return False






if __name__ == "__main__":
    pass