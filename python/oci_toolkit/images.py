import oci

from rich.console import Console
from rich.table import Table

console = Console()

def list_images():

    config = oci.config.from_file()

    identity_client = oci.identity.IdentityClient(config)

    compute_client = oci.core.ComputeClient(config)

    table = Table(title="OCI Images")

    table.add_column("Display Name", style="cyan")
    table.add_column("OS", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Image OCID", style="magenta")

    compartments = identity_client.list_compartments(
        config["tenancy"],
        compartment_id_in_subtree=True
    ).data

    root = identity_client.get_compartment(
        config["tenancy"]
    ).data

    compartments.append(root)

    for compartment in compartments:

        try:

            images = compute_client.list_images(
                compartment.id
            ).data

            for image in images[:15]:

                table.add_row(
                    image.display_name,
                    image.operating_system,
                    image.operating_system_version,
                    image.id
                )

        except Exception:
            pass

    console.print(table)
