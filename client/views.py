from django.http import FileResponse
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from concreteClassifierApp.settings import BASE_DIR
from concrete.ml.deployment import FHEModelClient
import os
import subprocess
import shutil
from shutil import copyfile
from pandas import DataFrame as pd
from pandas import read_csv

# Create your views here.
def index(request):
    return render(request, 'index.html')

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
    with open(os.path.join(BASE_DIR, f"client/Dashing/temporary/{id}.fasta"), "w") as output_file:
        output_file.write(first_line)
        output_file.write("\n")
        output_file.write(sequence)

def use_dashing():
    """Calls the appropriate Dashing commands on the files in the client/Dashing/temporary folder. Results in a CSV file containing the extracted features from the sequence and the accession ID."""
    subprocess.call(['sh', os.path.join(BASE_DIR, f"client/Dashing/dashingShell.sh")])

def process_dashing(request):
    """Function called by client to dash their .fasta files, creating a CSV file containing their sequence converted to numeric values for classification."""
    if request.method == "POST":

        clean_dashing_folder()

        fasta_fpath = request.FILES['file']

        fasta_firstline, truncate_output, id = read_truncate_sequence(fasta_fpath=fasta_fpath)

        write_fasta(id, fasta_firstline, truncate_output)

        use_dashing()

        dashing_output = os.path.join(BASE_DIR, f"client/Dashing/output.csv")

        drop_columns(dashing_output)

        #context = {'truncate_output':truncate_output ,'truncate_output_length':len(truncate_output), 'accession_id':id, 'metadata':fasta_firstline}
    
        #return render(request, 'upload_success.html', context)

        response = FileResponse(open(dashing_output, "rb"), as_attachment=True)

        return response

def process_encrypt(request):
    """The function called by the client-side application to facilitate encryption of their dashed .fasta file (which is now a CSV file)."""
    serialized_evaluation_keys, fhemodel_client = client_generate_keys()
    client_send_eval_keys_to_server(serialized_evaluation_keys)
    encrypted_data = encrypt_data(request, fhemodel_client)

    # setting encrypted data in session storage ()

    return render(request, "upload_success.html", context={'dict':{'keys':serialized_evaluation_keys, 'data':encrypted_data}})

def client_generate_keys():
    """Key generation method for the client-side application. Uses the client.zip file stored in the 'Compiled Model' folder"""
    # Let's create the client and load the model
    model_dir = os.path.join(BASE_DIR, rf'Compiled Model')
    key_dir = os.path.join(BASE_DIR, rf'Compiled Model/keys')

    if(os.listdir(key_dir)):
        for f in os.listdir(key_dir):
            shutil.rmtree(os.path.join(key_dir, f))

    fhemodel_client = FHEModelClient(model_dir, key_dir=key_dir)

    # The client first need to create the private and evaluation keys.
    fhemodel_client.generate_private_and_evaluation_keys()

    # Get the serialized evaluation keys
    serialized_evaluation_keys = fhemodel_client.get_serialized_evaluation_keys()

    # Check the size of the evaluation keys (in MB)
    #print(f"Evaluation keys size: {len(serialized_evaluation_keys) / (10**6):.2f} MB")

    return serialized_evaluation_keys, fhemodel_client

def send_client_specs():
    """Starts a download on the client's machine for the client specifications, if they want to perform the encryption offline."""
    filepath = os.path.join(BASE_DIR, rf'Compiled Model/client.zip')
    response = FileResponse(open(filepath, "rb"), as_attachment=True)
    return response

def client_send_eval_keys_to_server(eval_keys):
    """Send keys to the server application (classifier). May not be necessary if the keys are saved in the shared media folder."""
    #shutil.copyfile(os.path.join(BASE_DIR, rf'Compiled Model/keys'), os.path.join(BASE_DIR, "classifier/keys/"))
    with open(os.path.join(BASE_DIR, rf'classifier/keys/serialized_evaluation_keys.ekl'), "wb") as f:
            f.write(eval_keys)

def clean_dashing_folder():
    """Cleans the folder that hosts the uploaded .fasta file for Dashing (client-side only). Ensures that the data of only one upload is stored in the folder at a time."""
    dashing_dir = os.path.join(BASE_DIR, f"client/Dashing")
    dashing_temp_dir = os.path.join(BASE_DIR, f"client/Dashing/temporary")

    if(os.listdir(dashing_temp_dir)):
        for f in os.listdir(dashing_temp_dir):
            os.remove(os.path.join(dashing_temp_dir, f))
        os.remove(os.path.join(dashing_dir, "output.csv"))

def drop_columns(file, features_txt = os.path.join(BASE_DIR, "selected features.txt")):
    """Takes the output CSV file and drops the non-selected (based on prior feature seleciton) columns specified in the 'list' argument."""
    with open(features_txt, "r") as feature_file:
        temp_list = list(f for f in feature_file.read().splitlines())

    feature_list = ["Accession ID"] + temp_list

    drop_df = read_csv(file)
    drop_df = drop_df[[column for column in feature_list]] 
    drop_df.to_csv(os.path.join(BASE_DIR, "client/Dashing/output.csv"), index=False, header=True)

    #print(drop_df.columns.values.tolist())

def encrypt_data(request, fhemodel_client):
    df = read_csv(request.FILES['file'])
    #arr = df.to_numpy(dtype="uint16")
    arr_no_id = df.drop(columns=['Accession ID']).to_numpy(dtype="uint16")

    # with open(os.path.join(BASE_DIR, "selected features.txt"), "r") as feature_file:
    #      features = list(f for f in feature_file.read().splitlines())

    encrypted_rows = []

    for row in range(0, arr_no_id.shape[0]):
        #clear_input = arr[:,1:]
        clear_input = arr_no_id[[row],:]
        print(clear_input)
        encrypted_input = fhemodel_client.quantize_encrypt_serialize(clear_input)
        encrypted_rows.append(encrypted_input)
    
    return encrypted_rows