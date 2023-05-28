import shutil
from django.http import FileResponse
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from .models import Submission
from .forms import SubmissionForm
from concreteClassifierApp.settings import BASE_DIR
import os
import io, zipfile, requests
import subprocess
from pandas import DataFrame as pd
from pandas import read_csv
from concrete.ml.deployment import FHEModelServer

# Create your views here.
def index(request):
    form = SubmissionForm()
    context = {'form':form}
    return render(request, 'client/index.html', context=context)

def show_input(request):
    if request.method == 'POST':
        form_input = {key:value for key, value in request.POST.items()}
        file_input = {key:value for key, value in request.FILES.items()}
        
        print(form_input)

        return render(request, 'show_input.html', {'form_input':form_input, 'file_input':file_input})

def read_truncate_sequence(fasta_fpath):
    """Opens a FASTA file (pre-validated) and truncates the sequence, returning the ID and the truncated sequence as a string. 
    This ID and string should be ready for Dashing and converting to a CSV file for training."""
    truncated_seq = b""

    for line in fasta_fpath.readlines(): #chunks() method is essentially opening the file in binary mode.
        if b">" not in line:

            #print(f"New chunk: {line[-1]}")

            to_add = line.decode().strip().replace('\n', '').encode()
            #print(f"New line found: {to_add.decode()}")

            truncated_seq += to_add
        else:
            print("> found.")
            first_line = line.decode() 
            id = line.decode().split("|")[1].strip().replace('EPI_ISL_', '')

    decoded_truncated_seq = truncated_seq.decode()[20000:]

    return first_line, decoded_truncated_seq, id

def write_fasta(id, first_line, sequence):
    """Creates a FASTA file in the Dashing/temporary folder for use in the Dashing function."""
    with open(os.path.join(BASE_DIR, f"classifier/Dashing/temporary/{id}.fasta"), "w") as output_file:
        output_file.write(first_line)
        output_file.write("\n")
        output_file.write(sequence)

def use_dashing():
    """Calls the appropriate Dashing commands on the files in the classifier/Dashing/temporary folder. Results in a CSV file containing the extracted features from the sequence and the accession ID."""
    subprocess.call(['sh', os.path.join(BASE_DIR, f"classifier/Dashing/dashingShell.sh")])

def process_submit(request):
    if request.method == "POST":

        fasta_fpath = request.FILES['file']

        fasta_firstline, truncate_output, id = read_truncate_sequence(fasta_fpath=fasta_fpath)

        write_fasta(id, fasta_firstline, truncate_output)

        use_dashing()

        dashing_output = os.path.join(BASE_DIR, f"classifier/Dashing/output.csv")

        drop_columns(dashing_output)

        context = {'truncate_output':truncate_output ,'truncate_output_length':len(truncate_output), 'accession_id':id, 'metadata':fasta_firstline}
    
    return render(request, 'upload_success.html', context)

def client_generate_keys(request):
    pass

def send_client_specs(request):
    filepath = os.path.join(BASE_DIR, rf'Compiled Model/client.zip')
    response = FileResponse(open(filepath, "rb"), as_attachment=True)
    return response

def drop_columns(file, features_txt = os.path.join(BASE_DIR, "selected features.txt")):
    """Takes the output CSV file and drops the non-selected columns specified in the 'list' argument."""
    with open(features_txt, "r") as feature_file:
        temp_list = list(f for f in feature_file.read().splitlines())

    feature_list = ["Accession ID"] + temp_list

    drop_df = read_csv(file)
    drop_df = drop_df[[column for column in feature_list]]
    drop_df.to_csv(os.path.join(BASE_DIR, "classifier/Dashing/output.csv"), index=False, header=True)

    #print(drop_df.columns.values.tolist())

def start_classification(encrypted_data):

    count = 0
    model_path =os.path.join(BASE_DIR, "Compiled Model") 
    keys_path = os.path.join(BASE_DIR, "classifier/keys")
    keys_file = os.path.join(keys_path, "serialized_evaluation_keys.ekl")
    pred_dir = os.path.join(BASE_DIR, "classifier/predictions")

    data = encrypted_data
    #del request.session['data_dict']

    enc_file_list = []

    #print(data)

    for encrypted_input in data:
        with open(keys_file, "rb") as f:
            count += 1
            serialized_evaluation_keys = f.read()
            encrypted_prediction = FHEModelServer(model_path).run(encrypted_input, serialized_evaluation_keys)
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
    #buffer = io.BytesIO()
    #zip_file = zipfile.ZipFile(buffer, 'w')
    zip_file = zipfile.ZipFile(zip_filename, 'w')
    
    for filename in file_list:

        count += 1
        with open(filename, "rb") as file_read:
            zip_file.write(filename, f"encrypted_prediction_{count}.enc")
    zip_file.close()

    return zip_file

    # #craft download response    
    # resp = HttpResponse(buffer.getvalue(), content_type = "application/x-zip-compressed")
    # resp['Content-Disposition'] = f'attachment; filename={zip_filename}'

    # return resp


