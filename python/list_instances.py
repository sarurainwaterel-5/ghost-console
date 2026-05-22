import oci

# Load OCI config
config = oci.config.from_file()

# Create clients
identity_client = oci.identity.IdentityClient(config)
compute_client = oci.core.ComputeClient(config)

# Get tenancy info
tenancy_id = config["tenancy"]

print("\n=== OCI Compute Inventory ===\n")

# List compartments
compartments = identity_client.list_compartments(
    tenancy_id,
    compartment_id_in_subtree=True
).data

# Include root compartment
root_compartment = identity_client.get_compartment(tenancy_id).data
compartments.append(root_compartment)

# Loop through compartments
for compartment in compartments:
    print(f"\nCompartment: {compartment.name}")

    try:
        instances = compute_client.list_instances(
            compartment.id
        ).data

        if not instances:
            print("  No compute instances found.")
            continue

        for instance in instances:
            print(f"  Name:  {instance.display_name}")
            print(f"  State: {instance.lifecycle_state}")
            print(f"  Shape: {instance.shape}")
            print()

    except Exception as e:
        print(f"  Error: {e}")
