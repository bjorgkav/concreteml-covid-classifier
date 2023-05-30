from concrete.ml.deployment import FHEModelClient
import os
import numpy
from concreteClassifierApp.settings import BASE_DIR

# Let's check the results and compare them against the clear model

fhemodel_client = FHEModelClient(os.path.join(BASE_DIR, rf'Compiled Model'), key_dir=os.path.join(BASE_DIR, rf'Compiled Model/keys'))

decrypted_predictions = []

classes_dict = {0: 'B.1.1.529 (Omicron)', 1: 'B.1.617.2 (Delta)', 2: 'B.1.621 (Mu)', 3: 'C.37 (Lambda)'}

with open(os.path.join(BASE_DIR, "classifier/predictions/encrypted_prediction_1.enc"), "rb") as f:
    decrypted_prediction = fhemodel_client.deserialize_decrypt_dequantize(f.read())[0]
    decrypted_predictions.append(decrypted_prediction)
    decrypted_predictions_classes = numpy.array(decrypted_predictions).argmax(axis=1)
    # accuracy = (clear_prediction_classes == decrypted_predictions_classes).mean()
    # print(f"Accuracy between FHE prediction and clear model is: {accuracy*100:.0f}%")
    print([classes_dict[output] for output in decrypted_predictions_classes])