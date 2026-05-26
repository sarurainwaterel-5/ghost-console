import os
import socket
import subprocess
import psutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def system_status():

    hostname = socket.gethostname()

    local_ip = socket.gethostbyname(hostname)

    cpu_usage = psutil.cpu_percent(interval=1)

    ram = psutil.virtual_memory()

    disk = psutil.disk_usage('/')

    uptime_seconds = int(psutil.boot_time())

    docker_status = "Unknown"

    try:

        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            docker_status = "Running"

        else:
            docker_status = "Stopped"

    except Exception:
        docker_status = "Not Installed"

    oci_status = "Connected" if os.path.exists(
        os.path.expanduser("~/.oci/config")
    ) else "Missing"

    console.print(
        Panel.fit(
            "Ghost Console System Status",
            style="bold cyan"
        )
    )

    table = Table(title="Operational Status")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Hostname", hostname)

    table.add_row("Local IP", local_ip)

    table.add_row("CPU Usage", f"{cpu_usage}%")

    table.add_row(
        "RAM Usage",
        f"{ram.percent}%"
    )

    table.add_row(
        "Disk Usage",
        f"{disk.percent}%"
    )

    table.add_row(
        "Docker",
        docker_status
    )

    table.add_row(
        "OCI Config",
        oci_status
    )

    console.print(table)

