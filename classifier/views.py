import shutil
from django.http import FileResponse
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from concreteClassifierApp.settings import BASE_DIR
import os
import io, zipfile, requests
import subprocess
from pandas import DataFrame as pd
from pandas import read_csv
from concrete.ml.deployment import FHEModelServer

# Create your views here.
def index(request):
    
    return render(request, 'index.html', context={'classes_list':{0: 'B.1.1.529 (Omicron)', 1: 'B.1.617.2 (Delta)', 2: 'B.1.621 (Mu)', 3: 'C.37 (Lambda)'}})

def start_classification(request):

    clean_predictions_folder()

    count = 0
    model_path = os.path.join(BASE_DIR, "Compiled Model") 
    keys_path = os.path.join(BASE_DIR, "classifier/keys")
    keys_file = request.FILES['keys_file']
    pred_dir = os.path.join(BASE_DIR, "classifier/predictions")

    data = request.FILES['inputs'].read().strip()

    enc_file_list = []

    print(f"Data received from client is {data[:200]}")
    count += 1
    serialized_evaluation_keys = keys_file.read()
    encrypted_prediction = FHEModelServer(model_path).run(data, serialized_evaluation_keys)
    pred_file_name = f"encrypted_prediction_{count}.enc"
    pred_file_path = os.path.join(pred_dir, pred_file_name)
    with open(pred_file_path, "wb") as f:
        f.write(encrypted_prediction)

    #send all predictions as a zip file to client
    enc_file_list.append(pred_file_path)

    zipfile = create_zip(enc_file_list)

    return zipfile

def create_zip(file_list):
    count = 0
    zip_filename = os.path.join(BASE_DIR, "classifier/predictions/enc_predictions.zip")
    zip_download_name = "enc_predictions.zip"
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    #zip_file = zipfile.ZipFile(zip_filename, 'w')
    
    for filename in file_list:
        count += 1
        with open(filename, "rb") as file_read:
            zip_file.write(filename, f"encrypted_prediction_{count}.enc")
    zip_file.close()

    #craft download response    
    resp = HttpResponse(buffer.getvalue(), content_type = "application/force-download")
    resp['Content-Disposition'] = f'attachment; filename={zip_download_name}'

    return resp

def clean_predictions_folder():
    pred_dir = os.path.join(BASE_DIR, f"classifier/predictions")

    if(os.listdir(pred_dir)):
        for f in os.listdir(pred_dir):
            os.remove(os.path.join(pred_dir, f))