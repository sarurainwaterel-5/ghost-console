import oci

from rich.console import Console
from rich.table import Table

console = Console()

def list_ads():

    config = oci.config.from_file()

    identity_client = oci.identity.IdentityClient(config)

    ads = identity_client.list_availability_domains(
        config["tenancy"]
    ).data

    table = Table(title="OCI Availability Domains")

    table.add_column("Availability Domain", style="cyan")

    for ad in ads:

        table.add_row(
            ad.name
        )

    console.print(table)
