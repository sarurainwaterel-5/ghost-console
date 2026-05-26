import subprocess
import time
import socket
import psutil

from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()

def build_table():

    hostname = socket.gethostname()

    cpu = psutil.cpu_percent(interval=0.5)

    ram = psutil.virtual_memory()

    disk = psutil.disk_usage('/')

    net = psutil.net_io_counters()

    uptime = int(time.time() - psutil.boot_time())
    cpu_temp = "Unavailable"

    try:

        temp_output = subprocess.check_output(
            ["sensors"],
            text=True
        )

        for line in temp_output.splitlines():

            if "Package id 0" in line:

                cpu_temp = line.split("+")[1].split("°")[0] + "°C"

                break

    except Exception:
        pass
    docker_count = "0"
    docker_names = []

    try:

        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            docker_names = result.stdout.strip().splitlines()

            docker_count = str(len(docker_names))

    except Exception:
        pass	

    table = Table(title="Ghost Console Live Monitor")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Hostname", hostname)

    table.add_row("CPU Usage", f"{cpu}%")

    table.add_row(
        "RAM Usage",
        f"{ram.percent}%"
    )

    table.add_row(
        "Disk Usage",
        f"{disk.percent}%"
    )

    table.add_row(
        "Bytes Sent",
        str(net.bytes_sent)
    )

    table.add_row(
        "Bytes Received",
        str(net.bytes_recv)
    )

    table.add_row(
        "Uptime (sec)",
        str(uptime)
    )
    table.add_row(
        "Docker Containers",
        docker_count
    )

    if docker_names:

        table.add_row(
            "Container Names",
            ", ".join(docker_names)
        )
    table.add_row(
        "CPU Temp",
        cpu_temp
    )
    return table

def live_monitor():

    with Live(build_table(), refresh_per_second=1) as live:

        while True:

            time.sleep(1)

            live.update(build_table())
