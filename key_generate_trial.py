from concrete.ml.deployment import FHEModelClient, FHEModelDev, FHEModelServer

# Let's create the client and load the model
fhemodel_client = FHEModelClient("./Compiled Model", key_dir="")

# The client first need to create the private and evaluation keys.
fhemodel_client.generate_private_and_evaluation_keys()

# Get the serialized evaluation keys
serialized_evaluation_keys = fhemodel_client.get_serialized_evaluation_keys()