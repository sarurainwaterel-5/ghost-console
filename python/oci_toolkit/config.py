import oci


def get_config():

    return oci.config.from_file()


def get_identity_client():

    config = get_config()

    return oci.identity.IdentityClient(config)


def get_compute_client():

    config = get_config()

    return oci.core.ComputeClient(config)


def get_network_client():

    config = get_config()

    return oci.core.VirtualNetworkClient(config)
