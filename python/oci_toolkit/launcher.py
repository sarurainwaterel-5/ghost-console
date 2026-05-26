import oci

from rich.console import Console
from rich.panel import Panel

console = Console()

def launch_instance():

    config = oci.config.from_file()

    identity_client = oci.identity.IdentityClient(config)

    compute_client = oci.core.ComputeClient(config)

    network_client = oci.core.VirtualNetworkClient(config)

    console.print(
        Panel.fit(
            "Ghost Console OCI Instance Launcher",
            style="bold cyan"
        )
    )

    # Availability Domain
    ads = identity_client.list_availability_domains(
        config["tenancy"]
    ).data

    ad = ads[0].name

    console.print(
        f"[bold green]Using Availability Domain:[/bold green] {ad}"
    )

    # Get Compartments
    compartments = identity_client.list_compartments(
        config["tenancy"],
        compartment_id_in_subtree=True
    ).data

    root = identity_client.get_compartment(
        config["tenancy"]
    ).data

    compartments.append(root)

    subnet_id = None

    # Find first subnet
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

                if subnets:
                    subnet_id = subnets[0].id
                    break

        except Exception:
            pass

    if not subnet_id:

        console.print("[red]No subnet found[/red]")
        return

    console.print(
        f"[bold blue]Subnet Found:[/bold blue] {subnet_id}"
    )

    # Read SSH public key
    with open("/home/rain/.ssh/id_ed25519.pub", "r") as key_file:

        ssh_public_key = key_file.read()

    console.print(
        "[bold green]SSH public key loaded[/bold green]"
    )

    console.print(
        "[bold yellow]Provisioning logic coming next...[/bold yellow]"
    )
