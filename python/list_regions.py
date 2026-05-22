import oci

config = oci.config.from_file()

identity = oci.identity.IdentityClient(config)

regions = identity.list_regions()

print("\nOracle Cloud Regions:\n")

for region in regions.data:
    print(f"- {region.name}")
