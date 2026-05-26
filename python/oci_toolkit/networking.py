import oci

from rich.console import Console
from rich.table import Table

console = Console()

def list_networking():

    config = oci.config.from_file()

    identity_client = oci.identity.IdentityClient(config)

    network_client = oci.core.VirtualNetworkClient(config)

    table = Table(title="OCI Networking Inventory")

    table.add_column("VCN", style="cyan")
    table.add_column("Subnet", style="green")
    table.add_column("CIDR", style="yellow")

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

            vcns = network_client.list_vcns(
                compartment.id
            ).data

            for vcn in vcns:

                subnets = network_client.list_subnets(
                    compartment.id,
                    vcn_id=vcn.id
                ).data

                for subnet in subnets:

                    table.add_row(
                        vcn.display_name,
                        subnet.display_name,
                        subnet.cidr_block
                    )

        except Exception:
            pass

    console.print(table)
