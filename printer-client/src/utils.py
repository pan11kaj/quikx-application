import win32print,subprocess
import requests,json,asyncio
from collections import deque


def list_printers():
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL or win32print.PRINTER_ENUM_CONNECTIONS)
    return printers

def get_default_printer():
    return win32print.GetDefaultPrinter()



def decode_job_status(status_code: int) -> list[str]:
    JOB_STATUS_MAP = {
    win32print.JOB_STATUS_PAUSED: "Paused",
    win32print.JOB_STATUS_ERROR: "Error",
    win32print.JOB_STATUS_DELETING: "Deleting",
    win32print.JOB_STATUS_SPOOLING: "Spooling",
    win32print.JOB_STATUS_PRINTING: "Printing",
    win32print.JOB_STATUS_OFFLINE: "Offline",
    win32print.JOB_STATUS_PAPEROUT: "Paper Out",
    win32print.JOB_STATUS_PRINTED: "Printed",
    win32print.JOB_STATUS_DELETED: "Deleted",
    win32print.JOB_STATUS_BLOCKED_DEVQ: "Blocked",
    win32print.JOB_STATUS_USER_INTERVENTION: "User Intervention",
    win32print.JOB_STATUS_RESTART: "Restarting",
    win32print.JOB_STATUS_COMPLETE: "Complete",
    win32print.JOB_STATUS_RETAINED: "Retained",
    win32print.JOB_STATUS_RENDERING_LOCALLY: "Rendering Locally",
}
    """Convert status bitmask to readable status list."""
    if status_code == 0:
        return ["Queued"]

    statuses = []
    for code, label in JOB_STATUS_MAP.items():
        if status_code & code:
            statuses.append(label)

    return statuses


def get_print_jobs_with_status(printer_name: str):
    """
    Returns a list of print jobs with job_id, document name, and status.
    """
    jobs_info = []

    printer = win32print.OpenPrinter(printer_name)
    try:
        jobs = win32print.EnumJobs(
            printer,
            0,      # first job
            -1,     # all jobs
            2       # JOB_INFO_2 (detailed)
        )

        for job in jobs:
            jobs_info.append({
                "job_id": job["JobId"],
                "document": job["pDocument"],
                "user": job["pUserName"],
                "status": decode_job_status(job["Status"]),
                "pages": job["TotalPages"],
            })

    finally:
        win32print.ClosePrinter(printer)

    return jobs_info

# change this function by cups in linux
def print_file(printer,sumatra,file,ws,app, specifications=None):

    # data structure of specification:
    """
    specifications:
    [
        {'page':'2', copies:n} .... n
    ]
    """
    if specifications ==None:
        command = [
            sumatra,
            '-print-to',printer,
            file
        ]
       
    else:
        for jobs in specifications:
            command = [
                sumatra,
                '-print-to',printer,
                '-print-settings',f'page-ranges={jobs["page"]},copies={jobs["copies"]}',
                file
            ]
            subprocess.Popen(command)

def download_file(server_name,file_name):
    response = requests.get(server_name+"/static-files/"+file_name,stream=True)
    response.raise_for_status()
    try:
        with open(f"uploaded-files/{file_name}","wb") as f:
            for chuck in response.iter_content(chunk_size=8192):
                f.write(chuck)
            f.close()
        return 1
    except: 
        return False






if __name__ == "__main__":
    pass