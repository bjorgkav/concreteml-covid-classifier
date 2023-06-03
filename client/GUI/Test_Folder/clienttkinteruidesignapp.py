#!/usr/bin/python3
import shutil, subprocess, zipfile, requests
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkLabel,
    IntVar,
    StringVar,
    CTkTextbox,
    set_appearance_mode,
    set_default_color_theme)

from tkinter import filedialog as fd
from tkinter import END, INSERT
from datetime import date
from concrete.ml.deployment import FHEModelClient
import os, requests, stat, numpy, traceback, csv
from pandas import DataFrame as pd
from pandas import read_csv
from numpy import save

#region class
class ClientTkinterUiDesignApp:
    def __init__(self, master=None):
        # initialize FHEModelClient and output dictionary
        self.fhe_model_client = FHEModelClient(os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "keys"))
        self.data_dictionary = {}

        # create required folders if not exists
        this_folder = os.path.dirname(__file__)

        required_folder_names = ["fastas", "keys", "predictions"]

        for name in required_folder_names:
            if not os.path.exists(os.path.join(this_folder, f"{name}")):
                os.mkdir(os.path.join(this_folder, f"{name}"))

        # build ui
        # build ui
        self.root = CTk(None)
        self.root.configure(padx=60, pady=10)
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        self.root.title(
            "FHE-Enabled SARS-CoV-2 Classifier System (Client-side)")
        self.encrypt_name_var = StringVar()
        self.decrypt_name_var = StringVar()
        self.title = CTkLabel(self.root)
        self.title.configure(
            bg_color="#035690",
            font=CTkFont(
                "roboto",
                20,
                None,
                "roman",
                False,
                False),
            justify="center",
            text='FHE-Enabled SARS-CoV-2 Classifier System (Client-side)')
        self.title.pack(anchor="n", fill="x", ipady=10, side="top")
        self.description_frame = CTkFrame(self.root)
        self.about_label = CTkLabel(self.description_frame)
        self.about_label.configure(
            font=CTkFont(
                "roboto",
                24,
                None,
                "roman",
                False,
                False),
            text='About')
        self.about_label.pack(expand=False, fill="both", pady=10, side="top")
        self.description_label = CTkLabel(self.description_frame)
        self.description_label.configure(
            justify="left",
            text='This tool allows clients to conver their FASTA files to a numerical format and encrypt them for classification \non the server-side application. \n\nOn startup, this app automatically downloads the required files and scripts for operations \n(est. size 50 MB, internet connection required).')
        self.description_label.pack(expand=False, fill="x", side="top")
        self.description_frame.pack(
            fill="both", ipady=10, padx=20, pady=20, side="top")
        self.dashing_frame = CTkFrame(self.root)
        self.dashing_label = CTkLabel(self.dashing_frame)
        self.dashing_label.configure(
            anchor="w",
            justify="left",
            text='Enter your fasta file filepath for processing:')
        self.dashing_label.grid(column=0, padx=10, pady=10, row=0, sticky="nw")
        self.dashing_filename = CTkEntry(self.dashing_frame)
        self.dashing_name_var = StringVar()
        self.dashing_filename.configure(
            exportselection=False,
            justify="left",
            state="disabled",
            takefocus=False,
            textvariable=self.dashing_name_var,
            width=460)
        self.dashing_filename.grid(column=0, padx=10, row=1)
        self.dashing_browse = CTkButton(self.dashing_frame, hover=True)
        self.dashing_browse.configure(hover_color="#299cd9", text='Browse...')
        self.dashing_browse.grid(column=2, padx=10, row=1)
        self.dashing_browse.configure(command=self.getDashingInput)
        self.dashing_begin = CTkButton(self.dashing_frame)
        self.dashing_begin.configure(
            hover_color="#299cd9",
            text='Submit for FHE Classificaiton',
            width=300)
        self.dashing_begin.grid(column=0, columnspan=3, pady=10, row=2)
        self.dashing_begin.configure(command=self.processData)
        self.dashing_frame.pack(
            anchor="w",
            fill="x",
            padx=20,
            pady=10,
            side="top")
        ctkframe2 = CTkFrame(self.root)
        self.app_output_label = CTkLabel(ctkframe2)
        self.app_output_label.configure(text='Output Window')
        self.app_output_label.pack(side="top")
        self.app_output = CTkTextbox(ctkframe2)
        self.app_output.configure(height=75, state="disabled")
        _text_ = 'App activity will be displayed here.'
        self.app_output.configure(state="normal")
        self.app_output.insert("0.0", _text_)
        self.app_output.configure(state="disabled")
        self.app_output.pack(expand=True, fill="both", padx=10, pady=10)
        ctkframe2.pack(expand=True, fill="both", padx=20, pady=10, side="top")

        # Main widget
        self.mainwindow = self.root

    def run(self):
        self.mainwindow.mainloop()

    def writeOutput(self, string, delete_switch = False):
        """Function for writing argument 'string' to the app's output window. Set argument 'delete_switch' to True to clear the window before printing."""
        self.app_output.configure(state="normal")
        if(delete_switch):
            self.app_output.delete("1.0", END) #tk.END
            self.app_output.insert("0.0", f"{string}\n\n")
        else:
            self.app_output.insert(INSERT, f"{string}\n\n")
        self.app_output.see(END)
        self.app_output.configure(state="disabled")

    def processData(self):
        self.beginDashing()
        self.beginEncryption()
        self.beginDecryption()

    def getDashingInput(self):
        dashing_filename = fd.askopenfilename()
        self.dashing_name_var.set(dashing_filename)

    def getEncryptInput(self):
        encrypt_filename = fd.askopenfilename()
        self.encrypt_name_var.set(encrypt_filename)

    def getDecryptInput(self):
        decrypt_filename = fd.askopenfilename()
        self.decrypt_name_var.set(decrypt_filename)

    def beginDashing(self):
        """Function to begin dashing the user's input. Expects the 'self.dashing_name_var' to point to a .fasta file or zip file. Outputs a CSV file for encryption."""
        try:
            if(os.listdir(os.path.join(os.path.dirname(__file__), "fastas"))):
                for f in os.listdir(os.path.join(os.path.dirname(__file__), "fastas")):
                    os.remove(os.path.join(os.path.join(os.path.dirname(__file__), "fastas"), f))

            self.writeOutput("Beginning Dashing...", False)
        
            filename = self.dashing_name_var.get()

            if filename.endswith(".zip"):
                # with zipfile.ZipFile(filename, "r") as zObject:
                #     for file in zObject.namelist():
                #         opened_file = zObject.open(file, "r")
                #         first_line, sequence, id = self.readTruncateZipSequence(opened_file.readlines())
                #         self.writeFastaBytes(id, first_line, sequence)
                    
                #     self.useDashing()

                #     self.writeOutput("Writing dashed sequences to output.csv in the current directory...")

                #     dashing_output = os.path.join(os.path.dirname(__file__), f"output.csv")
                #     self.dropColumns(dashing_output)
                #     self.encrypt_name_var.set(dashing_output)

                #     self.writeOutput("Dashing Completed!")
                raise Exception("ZIP file inputs for this application are still in development.")

            elif filename.endswith(".fasta"):
                first_line, sequence, id = self.readTruncateSequence(filename)
                self.writeFasta(id, first_line, sequence)
                self.useDashing()

                self.writeOutput("Writing dashed sequences to output.csv in the current directory...")

                dashing_output = os.path.join(os.path.dirname(__file__), f"output.csv")
                self.dropColumns(dashing_output)
                self.encrypt_name_var.set(dashing_output)

                self.writeOutput("Dashing Completed!")
            else:
                raise Exception("Invalid file type: supported file types include .fasta, .zip")
        except Exception as e:
            #self.writeOutput(f"Error: {str(e)}")
            self.writeOutput(traceback.format_exc())

    def beginEncryption(self):
        """Function to begin the encryption of the user's dashed SARS-CoV-2 sequences. Expects 'self.encrypt_name_var' to point to the CSV file containing dashed sequences. Outputs a text file and .ekl file for the encrypted inputs and serialized evaluation keys respectively in this app's directory."""
        try:

            for f in os.listdir(os.path.dirname(__file__)):
                if f.split("/")[-1] in ["encrypted_input.txt", "serialized_evaluation_keys.ekl"]:
                    os.remove(f)

            if(not self.encrypt_name_var.get().endswith(".csv")):
                raise Exception("Invalid file type. Only .csv files are supported.")
            
            self.ensureCacheExists()

            self.writeOutput("Generating Keys...", False)

            self.generateKeys()

            self.writeOutput("Key generation complete! Key files written to folder inside 'keys' directory.")

            self.writeOutput("Beginning encryption...")
            #dashing_output = os.path.join(os.path.dirname(__file__), "output.csv")
            dashing_output = self.encrypt_name_var.get()
            df = read_csv(dashing_output)
            arr_no_id = df.drop(columns=['Accession ID']).to_numpy(dtype="uint16")

            #encrypted rows for input to server
            encrypted_rows = []

            #encrypted dictionary for outputs
            count = 0
            for id in df['Accession ID']:
                self.data_dictionary[count] = {'id':id, 'result':''} 

            #print(self.data_dictionary)
            for row in range(0, arr_no_id.shape[0]):
                #clear_input = arr[:,1:]
                clear_input = arr_no_id[[row],:]

                #print(clear_input)
                encrypted_input = self.fhe_model_client.quantize_encrypt_serialize(clear_input)
                self.writeOutput(f"New row encrypted of {type(encrypted_input)}; adding to list of encrypted values...")
                encrypted_rows.append(encrypted_input)
            
            self.encrypted_rows = encrypted_rows
            
            # for row in encrypted_rows:
            #     print("Row: ", row[:10])

            self.writeOutput(f"Encryption complete! Here are the first 15 character of your encrypted output:\n{encrypted_rows[0][0:16]}")

            self.saveEncryptedOutput()

            self.writeOutput("Saved encrypted inputs and key files to 'encrypted_input.txt' and 'serialized_evaluation_keys.ekl' respectively.\nPlease do not move these files until after prediction.")

            app_url = "http://localhost:8000"

            client = requests.session()

            client.get(app_url)

            predictions_zip_name = self.sendEncryptRequestToServer(client=client)

            self.decrypt_name_var.set(predictions_zip_name)

        except Exception as e:
            self.writeOutput(f"Error: {traceback.format_exc()}")

    def sendEncryptRequestToServer(self, client):
        """Sends 'encrypted_input.txt' and 'serialized_evaluation_keys.ekl' (expected to be located in the same directory as the app) to the server-side app through the Python requests library. URL is currently set to localhost:8000 for development purposes."""
        
        app_url = "http://localhost:8000"

        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            csrftoken = client.cookies['csrf']

        #self.writeOutput(f"{type(self.encrypted_rows)}")

        eval_keys_file = open('serialized_evaluation_keys.ekl', "rb")
        inputs_file = open("encrypted_input.txt", "rb")
        request_data = dict(csrfmiddlewaretoken=csrftoken)
        request_files = dict(inputs=inputs_file, keys_file=eval_keys_file)
        
        self.writeOutput("Sending encrypted inputs and keys to server for classification...")

        self.writeOutput("Waiting for server's response...")

        #code to send the above files to "localhost:8000/{function_name}"
        request_output = client.post(f"{app_url}/start_classification", data = request_data, files=request_files, headers=dict(Referer=app_url), )

        if request_output.ok:
            self.writeOutput(f"Response Code {request_output.status_code}: Classification completed!")

            if("test.zip" in os.listdir(os.path.dirname(__file__))): os.remove(os.path.join(os.path.dirname(__file__), "test.zip"), timeout=(10, 10))

            with open(os.path.join(os.path.dirname(__file__), "predictions/enc_predictions.zip"), "wb") as z:
                z.write(request_output.content)

        return os.path.join(os.path.dirname(__file__), "predictions/enc_predictions.zip")

    def generateKeys(self):
        model_dir = os.path.dirname(__file__)
        key_dir = os.path.join(os.path.dirname(__file__), "keys")

        if(os.listdir(key_dir)):
            for f in os.listdir(key_dir):
                shutil.rmtree(os.path.join(key_dir, f))

        fhemodel_client = FHEModelClient(model_dir, key_dir=key_dir)

        # The client first need to create the private and evaluation keys.
        fhemodel_client.generate_private_and_evaluation_keys()

        # Get the serialized evaluation keys
        self.serialized_evaluation_keys = fhemodel_client.get_serialized_evaluation_keys()

    def saveEncryptedOutput(self):
        filename = "encrypted_input.txt"
        with open(os.path.join(os.path.dirname(__file__), filename), "wb") as enc_file:
            for line in self.encrypted_rows:
                enc_file.write(line)
                #enc_file.write(b'\n\n\n\n\n')
        
        with open(os.path.join(os.path.dirname(__file__), r'serialized_evaluation_keys.ekl'), "wb") as f:
            f.write(self.serialized_evaluation_keys)

    def dropColumns(self, dashing_output, file = os.path.join(os.path.dirname(__file__), "selected_features.txt")):
        with open(file, "r") as feature_file:
            features = [feature.strip() for feature in feature_file.readlines()]
        #print("Selected features:", features)

        feature_list = ["Accession ID"] + features

        drop_df = read_csv(dashing_output)
        drop_df = drop_df[[column.strip() for column in feature_list]]  
        drop_df.to_csv("./output.csv", index=False, header=True)

    def readTruncateSequence(self, fasta_fpath):
        truncated_seq = ""

        with open(fasta_fpath, "r") as f:
            for line in f.readlines(): #chunks() method is essentially opening the file in binary mode.
                if ">" not in line:

                    #print(f"New chunk: {line[-1]}")

                    to_add = line.strip().replace('\n', '')
                    #print(f"New line found: {to_add.decode()}")

                    truncated_seq += to_add
                else:
                    print("> found.")
                    first_line = line
                    id = line.split("|")[1].strip().replace('EPI_ISL_', '')

        decoded_truncated_seq = truncated_seq[20000:]

        return first_line, decoded_truncated_seq, id
    
    def readTruncateZipSequence(self, fasta_readlines):
        truncated_seq = b""
        for line in fasta_readlines: #chunks() method is essentially opening the file in binary mode.
            if b">" not in line:

                #print(f"New chunk: {line[-1]}")

                to_add = line.decode().strip().replace('\n', '').encode()
                #print(f"New line found: {to_add.decode()}")

                truncated_seq += to_add
            else:
                print("> found.")
                first_line = line
                id = line.split(b"|")[1].strip().replace(b'EPI_ISL_', b'').decode()

        decoded_truncated_seq = truncated_seq[20000:]

        return first_line, decoded_truncated_seq, id

    def writeFastaBytes(self, id, first_line, sequence):
        """Writes a .fasta BYTES file in the 'fastas' folder named after the fasta's ID and containing the truncated sequence."""
        fasta_folder = os.path.join(os.path.dirname(__file__), f"fastas")
        if not os.path.exists(fasta_folder):
            os.mkdir(fasta_folder)

        with open(os.path.join(fasta_folder, f"{id}.fasta"), "wb") as output_file:
            output_file.write(first_line)
            output_file.write(sequence)

    def writeFasta(self, id, first_line, sequence):
        """Writes a .fasta file in the 'fastas' folder named after the fasta's ID and containing the truncated sequence."""
        fasta_folder = os.path.join(os.path.dirname(__file__), f"fastas")
        if not os.path.exists(fasta_folder):
            os.mkdir(fasta_folder)

        with open(os.path.join(fasta_folder, f"{id}.fasta"), "w") as output_file:
            output_file.write(first_line)
            output_file.write(sequence)

    def useDashing(self):
        """Calls the appropriate shell scripts (dashingShell.sh) and files after giving them execution permissions."""

        #grant execution permissions
        st = os.stat('dashingShell.sh')
        os.chmod('dashingShell.sh', st.st_mode | stat.S_IEXEC)

        st = os.stat('dashing_s512')
        os.chmod('dashing_s512', st.st_mode | stat.S_IEXEC)

        st = os.stat('readHLLandWrite.sh')
        os.chmod('readHLLandWrite.sh', st.st_mode | stat.S_IEXEC)

        subprocess.call(['sh', "dashingShell.sh"])

    def beginDecryption(self):
        try:

            if not self.decrypt_name_var.get().endswith(".zip"):
                raise Exception("Invalid file type: Only .zip files are supported.")
            
            self.writeOutput("Beginning decryption of encrypted predictions recieved from server...")

            decrypted_predictions = []
            classes_dict = {0: 'B.1.1.529 (Omicron)', 1: 'B.1.617.2 (Delta)', 2: 'B.1.621 (Mu)', 3: 'C.37 (Lambda)'}
            pred_folder = os.path.join(os.path.dirname(__file__), "predictions")

            zip_name = self.decrypt_name_var.get() #os.path.join(pred_folder, "enc_predictions.zip") if os.listdir(pred_folder) else os.path.join(os.path.dirname(__file__), "enc_predictions.zip")

            with zipfile.ZipFile(zip_name, "r") as zObject:
                zObject.extractall(path=pred_folder)
            
            enc_file_list = [filename for filename in os.listdir(pred_folder) if filename.endswith(".enc")]

            for filename in enc_file_list:
                #print(filename)
                with open(os.path.join(pred_folder, filename), "rb") as f:
                    decrypted_prediction = self.fhe_model_client.deserialize_decrypt_dequantize(f.read())[0]
                    decrypted_predictions.append(decrypted_prediction)
            
            decrypted_predictions_classes = numpy.array(decrypted_predictions).argmax(axis=1)
            final_output = [classes_dict[output] for output in decrypted_predictions_classes]

            # print(final_output)
            # print(final_output[0])

            for i in range(len(final_output)):
                self.data_dictionary[i]['result'] = final_output[i]

            #print(self.data_dictionary)
            self.writeOutput("Prediction Results:")
            for dictionary in self.data_dictionary.values():
                self.writeOutput(f"ID {dictionary['id']}: {dictionary['result']}")

            self.writeOutput("Saving prediction results to output file...")
            #create a file to save the prediction into
            self.savePredictionResult()
            self.writeOutput("Saving completed! Thank you for using the tool!")


        except Exception as e:
            self.writeOutput(f"Error: {str(e)}")
        
    def savePredictionResult(self):
        # save as individual and then add to cache.csv
        self.ensureCacheExists()
        cache_name = os.path.join(os.path.dirname(__file__), f"predictions/cache.csv")
        cache_df = read_csv(cache_name)

        for dict in self.data_dictionary.values():
            print(dict)
            df = pd.from_dict({key: [str(value).split(" ")[0]] for key, value in dict.items()})
            #df = df.rename(columns={'id':'Accession ID', 'result':'Lineage'})
            output_name = f"prediction_result_{dict['id']}_{date.today()}.csv"
            df.to_csv(os.path.join(os.path.dirname(__file__), f"predictions/{output_name}"), index=False, header=True)
        
            # add your results into cache.csv
            # Open the CSV file in "append" mode
            with open(cache_name, 'a', newline='') as f:
                if(dict['id'] not in set(cache_df['id'])):
                    # Create a dictionary writer with the dict keys as column fieldnames
                    writer = csv.DictWriter(f, fieldnames=dict.keys())
                    # Append single row to CSV
                    writer.writerow(dict)

    def ensureCacheExists(self):
        # ensure "cache.csv" created in predictions folder
        cache_name = os.path.join(os.path.dirname(__file__), f"predictions/cache.csv")
        if not os.path.exists(cache_name):
            cache_df = pd(data={'id':[], 'result':[]})
            cache_df.to_csv(cache_name, index=False, header=True)

#endregion

#region functions outside the class

def getRequiredFiles():
    files = [
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/dashing_s512",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/dashingShell.sh",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/readHLLandWrite.sh",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/Compiled%20Model/client.zip",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/selected_features.txt",
        ]
    for file in files:
        print(file.split("/")[-1].replace("%20", " "))
        if file.split("/")[-1].replace("%20", " ") not in os.listdir(os.path.dirname(__file__)):
            download(file, os.path.dirname(__file__))
    
def download(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    filename = url.split('/')[-1].replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)

    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))
#endregion

if __name__ == "__main__":
    download_files = input("Would you like to download the required files? (Type Yes or No.) ")
    
    if(download_files.strip() in ["y", "yes", "YES", "Yes"]):
        getRequiredFiles()

    app = ClientTkinterUiDesignApp()
    app.run()
