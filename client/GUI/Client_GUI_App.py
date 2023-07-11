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
from datetime import date, datetime
from concrete.ml.deployment import FHEModelClient
import os, requests, stat, numpy, json, traceback
from pandas import DataFrame as pd
from pandas import read_csv
from sklearn.preprocessing import LabelEncoder

#for downloading
os.environ["server_url"] = "localhost:8000"

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
            text='This tool allows clients to convert their FASTA files to a numerical format and encrypt them for classification \non the server-side application. \n\nOn startup, this app automatically downloads the required files and scripts for operations \n(est. size 50 MB, internet connection required).')
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
            text='Submit for FHE Classification',
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
        self.app_pred_history = CTkTextbox(ctkframe2)
        self.app_pred_history.configure(height=75, state="disabled")
        _text_ = 'Prediction History:\n'
        self.app_pred_history.configure(state="normal")
        self.app_pred_history.insert("0.0", _text_)
        self.app_pred_history.configure(state="disabled")
        self.app_pred_history.pack(expand=True, fill="both", padx=10, pady=10)
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

    def writePredOutput(self, string, delete_switch = False):
        """Function for writing argument 'string' to the app's prediction output window. Set argument 'delete_switch' to True to clear the window before printing."""
        self.app_pred_history.configure(state="normal")
        if(delete_switch):
            self.app_pred_history.delete("1.0", END) #tk.END
            self.app_pred_history.insert("0.0", f"{string}\n")
        else:
            self.app_pred_history.insert(INSERT, f"{string}\n")
        self.app_pred_history.see(END)
        self.app_pred_history.configure(state="disabled")

    def get_size(self, file_path, unit='bytes'):
        file_size = os.path.getsize(file_path)
        exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
        if unit not in exponents_map:
            raise ValueError("Must select from \
            ['bytes', 'kb', 'mb', 'gb']")
        else:
            size = file_size / 1024 ** exponents_map[unit]
            return round(size, 3)

    def processData(self):
        self.getFeaturesAndClasses()
        self.writeOutput("", True)
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
            if filename.endswith(".fasta"):
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
            self.writeOutput(f"Error: {traceback.format_exc()}")

    def beginEncryption(self, check_size = False):
        """Function to begin the encryption of the user's dashed SARS-CoV-2 sequences. Expects 'self.encrypt_name_var' to point to the CSV file containing dashed sequences. Outputs a text file and .ekl file for the encrypted inputs and serialized evaluation keys respectively in this app's directory."""
        try:

            for f in os.listdir(os.path.dirname(__file__)):
                if f.split("/")[-1] in ["encrypted_input.txt", "serialized_evaluation_keys.ekl"]:
                    os.remove(f)

            if(not self.encrypt_name_var.get().endswith(".csv")):
                raise Exception("Invalid file type. Only .csv files are supported.")

            self.writeOutput("Generating Keys...", False)

            self.generateKeys()

            self.writeOutput("Key generation complete! Key files written to folder inside 'keys' directory.")

            self.writeOutput("Beginning encryption...")

            dashing_output = self.encrypt_name_var.get()
            df = read_csv(dashing_output)
            arr_no_id = df.drop(columns=['Accession ID']).to_numpy(dtype="uint16")

            #encrypted rows for input to server
            encrypted_rows = []

            #encrypted dictionary for outputs
            count = 0
            for id in df['Accession ID']:
                self.data_dictionary[count] = {'id':id, 'result':''} 

            for row in range(0, arr_no_id.shape[0]):
                self.encrypted_id = self.data_dictionary[row]['id']
                clear_input = arr_no_id[[row],:]

                encrypted_input = self.fhe_model_client.quantize_encrypt_serialize(clear_input)
                self.writeOutput(f"New row encrypted of {type(encrypted_input)}; adding to list of encrypted values...")
                encrypted_rows.append(encrypted_input)
            
            self.encrypted_rows = encrypted_rows

            self.writeOutput(f"Encryption complete! Here are the first 15 character of your encrypted output:\n{encrypted_rows[0][0:16]}")

            enc_filename = self.saveEncryptedOutput(self.encrypted_id)

            self.writeOutput("Saved encrypted inputs and key files to 'encrypted_input.txt' and 'serialized_evaluation_keys.ekl' respectively.\nPlease do not move these files until after prediction.")

            app_url = f"http://{os.environ['server_url']}"

            client = requests.session()

            client.get(app_url)

            predictions_zip_name = self.sendEncryptRequestToServer(enc_filename, client=client)

            self.decrypt_name_var.set(predictions_zip_name)

        except Exception as e:
            self.writeOutput(f"Error: {traceback.format_exc()}")

    def sendEncryptRequestToServer(self, encrypt_filename, client):
        """Sends 'encrypted_input.txt' and 'serialized_evaluation_keys.ekl' (expected to be located in the same directory as the app) to the server-side app through the Python requests library. URL is set to localhost:8000 in development."""
        
        app_url = f"http://{os.environ['server_url']}"

        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            csrftoken = client.cookies['csrf']

        eval_keys_file = open('serialized_evaluation_keys.ekl', "rb")
        inputs_file = open(encrypt_filename, "rb")
        request_data = dict(csrfmiddlewaretoken=csrftoken)
        request_files = dict(inputs=inputs_file, keys_file=eval_keys_file)
        
        self.writeOutput("Sending encrypted inputs and keys to server for classification...")

        self.writeOutput("Waiting for server's response...")

        #send the above files to "localhost:8000/{function_name}"
        request_output = client.post(f"{app_url}/start_classification", data = request_data, files=request_files, headers=dict(Referer=app_url), )

        if request_output.ok:
            self.writeOutput(f"Response Code {request_output.status_code}: Classification completed!")

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

        # The client first needs to create the private and evaluation keys.
        fhemodel_client.generate_private_and_evaluation_keys()

        # Get the serialized evaluation keys
        self.serialized_evaluation_keys = fhemodel_client.get_serialized_evaluation_keys()

    def saveEncryptedOutput(self, id, show_key_sizes = True):
        """Saves encrypted rows as a text file to send to the server for classification. Also shows key sizes for comparison by default."""
        filename = f"{id}_encrypted_input.txt"
        with open(os.path.join(os.path.dirname(__file__), filename), "wb") as enc_file:
            for line in self.encrypted_rows:
                enc_file.write(line)
        
        with open(os.path.join(os.path.dirname(__file__), r'serialized_evaluation_keys.ekl'), "wb") as f:
            f.write(self.serialized_evaluation_keys)

        if show_key_sizes:
            eval_key_size = self.get_size("./serialized_evaluation_keys.ekl", 'kb')
            print(f"Evaluation key size: {eval_key_size} kB")

            # Check the size of the evaluation keys (in MB)
            priv_key_size = self.get_size("./keys", 'kb')
            print(f"Private key size: {priv_key_size} kB")

        return filename

    def getFeaturesAndClasses(self, file = os.path.join(os.path.dirname(__file__), "features_and_classes.txt")):
        """Parses 'features_and_classes.txt' in the current directory and extracts a dictionary containing the selected features and the original class labels for decryption."""
        with open(file, "r") as fc_file:
            dictionary = json.loads(fc_file.readline())
            self.selected_features = dictionary["features"]
            self.classes_labels = dictionary["classes"]
            self.classes_labels = {int(key):value for key, value in self.classes_labels.items()}
            print(self.selected_features)
            print(self.classes_labels)

    def dropColumns(self, dashing_output):
        """Drops columns from the Dashing output based on the parsed selected features from getFeaturesAndClasses()."""
        features = self.selected_features
        feature_list = ["Accession ID"] + features

        drop_df = read_csv(dashing_output)
        drop_df = drop_df[[column.strip() for column in feature_list]]  
        drop_df.to_csv("./output.csv", index=False, header=True)

    def readTruncateSequence(self, fasta_fpath, verbose = False):
        """Reads the entire sequence from the input file and truncates it before creating a new FASTA file with the truncated sequence."""
        truncated_seq = ""

        with open(fasta_fpath, "r") as f:
            for line in f.readlines(): #chunks() method is essentially opening the file in binary mode.
                if ">" not in line:

                    to_add = line.strip().replace('\n', '')

                    truncated_seq += to_add
                else:
                    if verbose:
                        print("> found.")
                    if("|" not in line):
                        self.writeOutput("Warning: Please follow the recommended input file structure: >Reference/Database|AccessionID|DateCollected")
                        first_line = line
                        id = line.split(" ")[0].strip().replace('>', '')
                    else:
                        first_line = line
                        id = line.split("|")[1].strip()

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

    def verifyDashingIntegrity(self, list):
        """Checks if the Dashing files have been downloaded properly. Forces re-download as needed."""
        for dashing_file in list:
            try:
                mb_size = os.stat(dashing_file).st_size / (1024*1024)
                if(mb_size < 18): #dashing files should not be less than 18 mb
                    raise Exception("Dashing files may not have been downloaded correctly. Redownloading the files...")
            except Exception as e:
                self.writeOutput(str(e))
                getRequiredFiles(force_download=True)

    def useDashing(self):
        """Calls the appropriate shell scripts (dashingShell<bits>.sh) and files after giving them execution permissions. 
        Takes into account instruction set incompatibility and attempts to use lower-bit binary releases if possible."""

        files_to_allow = [
            os.path.join(os.path.dirname(__file__),'dashingShell512.sh'),
            os.path.join(os.path.dirname(__file__),'dashing_s512'),
            os.path.join(os.path.dirname(__file__),'readHLLandWrite512.sh'),
            os.path.join(os.path.dirname(__file__),'dashingShell256.sh'),
            os.path.join(os.path.dirname(__file__),'dashing_s256'),
            os.path.join(os.path.dirname(__file__),'readHLLandWrite256.sh'),
            os.path.join(os.path.dirname(__file__),'dashingShell128.sh'),
            os.path.join(os.path.dirname(__file__),'dashing_s128'),
            os.path.join(os.path.dirname(__file__),'readHLLandWrite128.sh'),
        ]

        files_to_verify = [
            os.path.join(os.path.dirname(__file__),'dashing_s512'),
            os.path.join(os.path.dirname(__file__),'dashing_s256'),
            os.path.join(os.path.dirname(__file__),'dashing_s128'),
        ]

        for f in files_to_allow:
            st = os.stat(f)
            os.chmod(f, st.st_mode | stat.S_IEXEC)

        self.verifyDashingIntegrity(files_to_verify)

        #calls the shell script and returns CalledProcessError if an exit code is not zero
        try:
            subprocess.check_output(['sh', 'dashingShell512.sh'])
        except subprocess.CalledProcessError as e:
            self.writeOutput(f"Error running default dashing_s512: {'OS must support AVX512BW instructions'}.")
            self.writeOutput("Trying dashing_s256...")
            try:
                subprocess.check_output(['sh', 'dashingShell256.sh'])
            except subprocess.CalledProcessError as e:
                self.writeOutput(f"Error running default dashing_s256: {'OS must support AVX2 instructions.'}")
                self.writeOutput("Trying dashing_s128...")
                try:
                    subprocess.check_output(['sh', 'dashingShell128.sh'])
                except subprocess.CalledProcessError as e:
                    self.writeOutput(f"Error running all dashing binaries: {'OS must support AVX512BW, AVX2, or SSE2 instructions'}")

    def beginDecryption(self):
        """Begins decryption of the encrypted prediction results received from the server after classification. Expects the input filepath (self.decrypt_name_var) to be a .zip file, and raises an error if not.
        Also saves the prediction results to a CSV file for viewing later."""
        try:

            if not self.decrypt_name_var.get().endswith(".zip"):
                raise Exception("Invalid file type: Only .zip files are supported. Was there an error the server?")
            
            self.writeOutput("Beginning decryption of encrypted predictions recieved from server...")

            decrypted_predictions = []

            #setting classes dictionary
            try:
                classes_dict = self.classes_labels
            except:
                classes_dict = {0: 'B.1.1.529 (Omicron)', 1: 'B.1.617.2 (Delta)', 2: 'B.1.621 (Mu)', 3: 'C.37 (Lambda)'}

            pred_folder = os.path.join(os.path.dirname(__file__), "predictions")

            zip_name = self.decrypt_name_var.get()

            with zipfile.ZipFile(zip_name, "r") as zObject:
                zObject.extractall(path=pred_folder)
            
            enc_file_list = [filename for filename in os.listdir(pred_folder) if filename.endswith(".enc")]

            for filename in enc_file_list:
                with open(os.path.join(pred_folder, filename), "rb") as f:
                    decrypted_prediction = self.fhe_model_client.deserialize_decrypt_dequantize(f.read())[0]
                    decrypted_predictions.append(decrypted_prediction)
            
            decrypted_predictions_classes = numpy.array(decrypted_predictions).argmax(axis=1)
            final_output = [classes_dict[output] for output in decrypted_predictions_classes]

            for i in range(len(final_output)):
                self.data_dictionary[i]['result'] = final_output[i]

            self.writeOutput("Prediction Results:")
            for dictionary in self.data_dictionary.values():
                self.writeOutput(f"ID {dictionary['id']}: {dictionary['result']}")
                self.writePredOutput(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} -- ID {dictionary['id']}: {dictionary['result']}")

            self.writeOutput("Saving prediction results to output file...")

            #create a file to save the prediction into
            self.savePredictionResult()
            self.writeOutput("Saving completed! Thank you for using the tool!")


        except Exception as e:
            self.writeOutput(f"Error: {str(e)}")
        
    def savePredictionResult(self):
        for dict in self.data_dictionary.values():
            print(dict)
            df = pd.from_dict({key: [str(value).split(" ")[0]] for key, value in dict.items()})
            output_name = f"prediction_result_{dict['id']}_{date.today()}.csv"
            df.to_csv(os.path.join(os.path.dirname(__file__), f"predictions/{output_name}"), index=False, header=True)
#endregion

#region functions outside the class

def getRequiredFiles(force_download = False):
    """Downloads the required files for the application. Set force_download to True to download the files even if present in the directory. Will be called if the Dashing binaries were not downloaded correctly.
    
    By default, targets the project's GitHub repository (see 'files' array) for downloading the files, but can be set to localhost:8000 to download from the local deployment server."""

    download_url = f"http://{os.environ['server_url']}/download?filename="

    files = [
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/dashing_s512",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/Compiled%20Model/client.zip",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/dashingShell512.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/dashingShell128.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/dashingShell256.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/readHLLandWrite512.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/readHLLandWrite128.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/readHLLandWrite256.sh",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/ClientDownloads/features_and_classes.txt",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/dashing_s128",
        # r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/AlternativeDashingDownloads/dashing_s256",
        "client.zip",
        "features_and_classes.txt",
        "dashing_s512",
        "dashingShell512.sh",
        "readHLLandWrite512.sh",
        "dashing_s256",
        "dashingShell256.sh",
        "readHLLandWrite256.sh",
        "dashing_s128",
        "dashingShell128.sh",
        "readHLLandWrite128.sh",
        ]
    
    for file in files:
        # parsed_name = file.split("/")[-1].replace("%20", " ")
        print(f"Checking current directory for file: {file}")
        if (file not in os.listdir(os.path.dirname(__file__))) or force_download:
            download(f"{download_url}{file}", os.path.dirname(__file__), file)
    
def download(url, dest_folder, dest_name):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_path = os.path.join(dest_folder, dest_name)

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
    getRequiredFiles()

    app = ClientTkinterUiDesignApp()
    app.run()
