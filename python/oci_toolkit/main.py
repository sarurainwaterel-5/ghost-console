import typer

from inventory import run_inventory

app = typer.Typer()

@app.command()
def inventory():
    run_inventory()

@app.command()
def launch():
    print("Launch module coming soon")

@app.command()
def network():
    print("Networking module coming soon")

if __name__ == "__main__":
    app()
