from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from .models import Submission
from .forms import SubmissionForm
from concreteClassifierApp.settings import BASE_DIR
import os
import subprocess

# Create your views here.
def index(request):
    form = SubmissionForm()
    context = {'form':form}
    return render(request, 'index.html', context=context)

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
    #subprocess.call(['sh', os.path.join(BASE_DIR, f"classifier/Dashing/dashing_s512 sketch -k31 -p13 -S9 {os.path.join(BASE_DIR, 'classifier/Dashing/temporary/*.fasta')}")])
    #subprocess.call(['sh', os.path.join(BASE_DIR, f"classifier/Dashing/readHLLandWrite.sh")])

def process_submit(request):
    if request.method == "POST":
        # create a submission entry and save it to the database
        # form = SubmissionForm(request.POST or None, request.FILES or None)
        # if form.is_valid():
        #     new_submission = form.save()
        #fasta_fpath = Submission.objects.get(id=new_submission.id).getFile()

        fasta_fpath = request.FILES['file']

        fasta_firstline, truncate_output, id = read_truncate_sequence(fasta_fpath=fasta_fpath)

        write_fasta(id, fasta_firstline, truncate_output)

        use_dashing()

        context = {'truncate_output':truncate_output ,'truncate_output_length':len(truncate_output), 'accession_id':id, 'metadata':fasta_firstline}
    
    return render(request, 'upload_success.html', context)

def client_generate_keys(request):
    pass