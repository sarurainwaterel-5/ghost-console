import csv
import json


from config import (
    get_config,
    get_identity_client,
    get_compute_client,
    get_network_client
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def run_inventory():

    # Load OCI config
    config = get_config()

    # Identity client
    identity_client = get_identity_client()

    # Get subscribed regions
    regions = identity_client.list_region_subscriptions(
        config["tenancy"]
    ).data

    # Inventory storage
    inventory_data = []

    total_instances = 0

    console.print(
        Panel.fit(
            "Ghost Console OCI Toolkit - Multi Region Inventory",
            style="bold cyan"
        )
    )

    # Loop through regions
    for region in regions:

        region_name = region.region_name

        console.print(
            f"\n[bold green]Scanning Region:[/bold green] {region_name}"
        )

        # Regional config
        regional_config = config.copy()
        regional_config["region"] = region_name

        # Regional clients
        compute_client = get_compute_client()

        network_client = get_network_client()

        # Rich table
        table = Table(title=f"OCI Inventory - {region_name}")

        table.add_column("Name", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Shape", style="yellow")
        table.add_column("Region", style="blue")
        table.add_column("Public IP", style="magenta")

        # Compartments
        compartments = identity_client.list_compartments(
            config["tenancy"],
            compartment_id_in_subtree=True
        ).data

        # Root compartment
        root = identity_client.get_compartment(
            config["tenancy"]
        ).data

        compartments.append(root)

        region_count = 0

        # Loop compartments
        for compartment in compartments:

            try:

                instances = compute_client.list_instances(
                    compartment.id
                ).data

                for instance in instances:

                    public_ip = "N/A"

                    try:

                        attachments = compute_client.list_vnic_attachments(
                            compartment.id,
                            instance_id=instance.id
                        ).data

                        for attachment in attachments:

                            vnic = network_client.get_vnic(
                                attachment.vnic_id
                            ).data

                            if vnic.public_ip:
                                public_ip = vnic.public_ip

                    except Exception:
                        pass

                    # Add table row
                    table.add_row(
                        instance.display_name,
                        instance.lifecycle_state,
                        instance.shape,
                        region_name,
                        public_ip
                    )

                    # Save inventory data
                    inventory_data.append({
                        "name": instance.display_name,
                        "state": instance.lifecycle_state,
                        "shape": instance.shape,
                        "region": region_name,
                        "public_ip": public_ip
                    })

                    total_instances += 1
                    region_count += 1

            except Exception as e:
                console.print(f"[red]{e}[/red]")

        console.print(table)

        console.print(
            f"[bold blue]Instances in {region_name}: {region_count}[/bold blue]"
        )

    # Export CSV
    if inventory_data:

        with open("inventory.csv", "w", newline="") as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=inventory_data[0].keys()
            )

            writer.writeheader()
            writer.writerows(inventory_data)

        # Export JSON
        with open("inventory.json", "w") as jsonfile:

            json.dump(
                inventory_data,
                jsonfile,
                indent=4
            )

        console.print(
            "\n[bold green]Exports created:[/bold green] inventory.csv, inventory.json"
        )

    console.print(
        f"\n[bold cyan]Total Instances Found:[/bold cyan] {total_instances}"
    )
