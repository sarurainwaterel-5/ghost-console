import csv
import json
import oci

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Load OCI config
config = oci.config.from_file()

# Identity client
identity_client = oci.identity.IdentityClient(config)

# Get subscribed regions
regions = identity_client.list_region_subscriptions(
    config["tenancy"]
).data

# Data storage
inventory = []
total_instances = 0

console.print(
    Panel.fit(
        "Ghost Console OCI Inventory Tool v3",
        style="bold cyan"
    )
)

# Loop through regions
for region in regions:

    region_name = region.region_name

    console.print(f"\n[bold green]Scanning Region:[/bold green] {region_name}")

    # Clone config for region
    regional_config = config.copy()
    regional_config["region"] = region_name

    # Regional clients
    compute_client = oci.core.ComputeClient(regional_config)
    network_client = oci.core.VirtualNetworkClient(regional_config)

    # Rich table
    table = Table(title=f"OCI Inventory - {region_name}")

    table.add_column("Name", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Shape", style="yellow")
    table.add_column("Public IP", style="magenta")

    # Compartments
    compartments = identity_client.list_compartments(
        config["tenancy"],
        compartment_id_in_subtree=True
    ).data

    # Add root compartment
    root = identity_client.get_compartment(
        config["tenancy"]
    ).data

    compartments.append(root)

    region_count = 0

    for compartment in compartments:

        try:
            instances = compute_client.list_instances(
                compartment.id
            ).data

            for instance in instances:

                # FILTER:
                # only show running instances
                if instance.lifecycle_state != "RUNNING":
                    continue

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
                    public_ip
                )

                # Save inventory
                inventory.append({
                    "region": region_name,
                    "compartment": compartment.name,
                    "name": instance.display_name,
                    "state": instance.lifecycle_state,
                    "shape": instance.shape,
                    "public_ip": public_ip
                })

                total_instances += 1
                region_count += 1

        except Exception as e:
            console.print(
                f"[red]Error:[/red] {e}"
            )

    console.print(table)

    console.print(
        f"[bold blue]Running instances in {region_name}: {region_count}[/bold blue]"
    )

# Export CSV
if inventory:

    with open("oci_inventory_v3.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=inventory[0].keys()
        )

        writer.writeheader()
        writer.writerows(inventory)

    # Export JSON
    with open("oci_inventory_v3.json", "w") as jsonfile:
        json.dump(inventory, jsonfile, indent=4)

console.print(
    f"\n[bold green]Total Running Instances Found:[/bold green] {total_instances}"
)

console.print(
    "[bold cyan]Exports Created:[/bold cyan] oci_inventory_v3.csv, oci_inventory_v3.json"
)
