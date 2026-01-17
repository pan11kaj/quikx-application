import cups

def print_active_job_queue():
    conn = cups.Connection()
    printer_name = conn.getDefault()
    jobs = conn.getJobs(which_jobs="active", my_jobs=False)

    # Filter jobs for default printer
    printer_jobs = {
        job_id: job
        for job_id, job in jobs.items()
        if job["printer-uri-supported"].endswith(printer_name)
    }

    if not printer_jobs:
        print("🟢 Printer is idle (no active jobs)")
        return

    # Sort by queue order
    sorted_jobs = sorted(
        printer_jobs.items(),
        key=lambda j: j[1].get("time-at-creation", 0)
    )

    print(f"\n📄 Active Job Queue for Printer: {printer_name}")
    print("-" * 50)

    for position, (job_id, job) in enumerate(sorted_jobs, start=1):
        state_code = job["job-state"]

        state_name = {
            3: "PENDING",
            4: "HELD",
            5: "PROCESSING",
            6: "STOPPED"
        }.get(state_code, "OTHER")

        print(
            f"#{position} | "
            f"Job ID: {job_id} | "
            f"State: {state_name} | "
            f"Name: {job['job-name']}"
        )


print_active_job_queue()