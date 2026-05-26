import typer
from monitor import live_monitor
from status import system_status
from ad import list_ads
from images import list_images
from networking import list_networking
from inventory import run_inventory
from launcher import launch_instance

app = typer.Typer()

@app.command()
def monitor():
    live_monitor()

@app.command()
def status():
    system_status()

@app.command()
def images():
    list_images()

@app.command()
def ads():
    list_ads()

@app.command()
def inventory():
    run_inventory()
@app.command()
def network():
    list_networking()

@app.command()
def launch():
    launch_instance()


if __name__ == "__main__":
    app()
