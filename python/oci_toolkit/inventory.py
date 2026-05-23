import csv
import json
import oci

from rich.console import Console
from rich.table import Table

console = Console()

def run_inventory():

    # Load OCI config
    config = oci.config.from_file()

    # OCI Clients
    identity_client = oci.identity.IdentityClient(config)

    compute_client = oci.core.ComputeClient(config)

    network_client = oci.core.VirtualNetworkClient(config)

    # Inventory storage
    inventory_data = []

    # Rich table
    table = Table(title="OCI Inventory")

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

    # Loop through compartments
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

                # Add to table
                table.add_row(
                    instance.display_name,
                    instance.lifecycle_state,
                    instance.shape,
                    config["region"],
                    public_ip
                )

                # Save inventory data
                inventory_data.append({
                    "name": instance.display_name,
                    "state": instance.lifecycle_state,
                    "shape": instance.shape,
                    "region": config["region"],
                    "public_ip": public_ip
                })

        except Exception as e:
            console.print(f"[red]{e}[/red]")

    # Display table
    console.print(table)

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
            "[bold green]Exports created:[/bold green] inventory.csv, inventory.json"
        )
