#!/usr/bin/python3
import subprocess
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkLabel,
    IntVar,
    StringVar,
    set_appearance_mode,
    set_default_color_theme)

from tkinter import filedialog as fd

from concrete.ml.deployment import FHEModelClient

import os, requests, stat

from pandas import DataFrame as pd
from pandas import read_csv

#region class
class ClientTkinterUiDesignApp:
    def __init__(self, master=None):
        # build ui
        self.root = CTk(None)
        self.root.configure(padx=60, pady=10)
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        self.root.geometry("800x550")
        self.root.resizable(True, True)
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
            text='Enter your fasta or zip filepath for Dashing:')
        self.dashing_label.grid(column=0, padx=10, pady=10, row=0, sticky="nw")
        self.dashing_name_var = StringVar()
        self.dashing_filename = CTkEntry(self.dashing_frame, textvariable=self.dashing_name_var)
        self.dashing_filename.configure(
            exportselection=False,
            justify="left",
            state="disabled",
            takefocus=False,
            width=460)
        self.dashing_filename.grid(column=0, padx=10, row=1)
        self.dashing_browse = CTkButton(self.dashing_frame, hover=True)
        self.dashing_browse.configure(hover_color="#299cd9", text='Browse...', command=self.getDashingInput)
        self.dashing_browse.grid(column=2, padx=10, row=1)
        self.dashing_begin = CTkButton(self.dashing_frame, command=self.beginDashing)
        self.dashing_begin.configure(
            hover_color="#299cd9",
            text='Begin dashing',
            width=300)
        self.dashing_begin.grid(column=0, columnspan=3, pady=10, row=2)
        self.dashing_frame.pack(
            anchor="w",
            fill="x",
            padx=20,
            pady=10,
            side="top")
        self.encrypt_frame = CTkFrame(self.root)
        self.encrypt_label = CTkLabel(self.encrypt_frame)
        self.encrypt_label.configure(
            anchor="w",
            justify="left",
            text='Enter your dashing output filepath for encryption:')
        self.encrypt_label.grid(column=0, padx=10, pady=10, row=0, sticky="nw")
        self.encrypt_name_var = StringVar()
        self.encrypt_filename = CTkEntry(self.encrypt_frame, textvariable=self.encrypt_name_var)
        self.encrypt_filename.configure(
            exportselection=False,
            justify="left",
            state="disabled",
            takefocus=False,
            width=460)
        self.encrypt_filename.grid(column=0, padx=10, row=1)
        self.encrypt_browse = CTkButton(self.encrypt_frame, hover=True, command=self.getEncryptInput)
        self.encrypt_browse.configure(hover_color="#299cd9", text='Browse...')
        self.encrypt_browse.grid(column=2, padx=10, row=1)
        self.encrypt_begin = CTkButton(self.encrypt_frame)
        self.encrypt_begin.configure(
            hover_color="#299cd9",
            text='Encrypt file',
            width=300)
        self.encrypt_begin.grid(column=0, columnspan=3, pady=10, row=2)
        self.encrypt_frame.pack(
            anchor="w",
            fill="x",
            padx=20,
            pady=10,
            side="top")

        # Main widget
        self.mainwindow = self.root

    def run(self):
        self.mainwindow.mainloop()

    def getDashingInput(self):
        dashing_filename = fd.askopenfilename()
        self.dashing_name_var.set(dashing_filename)

    def getEncryptInput(self):
        encrypt_filename = fd.askopenfilename()
        self.encrypt_name_var.set(encrypt_filename)

    def beginDashing(self):
        filename = self.dashing_name_var.get()
        first_line, sequence, id = self.readTruncateSequence(filename)
        self.writeFasta(id, first_line, sequence)
        self.useDashing()
        dashing_output = os.path.join(os.path.dirname(__file__), f"output.csv")
        self.dropColumns(dashing_output)

    def dropColumns(self, file, features_txt = "./selected features.txt"):
        with open(features_txt, "r") as feature_file:
            temp_list = list(f for f in feature_file.read().splitlines())

            feature_list = ["Accession ID"] + temp_list

            drop_df = read_csv(file)
            drop_df = drop_df[[column for column in feature_list]] 
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

    def writeFasta(self, id, first_line, sequence):
        fasta_folder = os.path.join(os.path.dirname(__file__), f"fastas")
        if not os.path.exists(fasta_folder):
            os.mkdir(fasta_folder)

        with open(os.path.join(fasta_folder, f"{id}.fasta"), "w") as output_file:
            output_file.write(first_line)
            output_file.write(sequence)

    def useDashing(self):

        #grant execution permissions
        st = os.stat('dashingShell.sh')
        os.chmod('dashingShell.sh', st.st_mode | stat.S_IEXEC)

        st = os.stat('dashing_s512')
        os.chmod('dashing_s512', st.st_mode | stat.S_IEXEC)

        st = os.stat('readHLLandWrite.sh')
        os.chmod('readHLLandWrite.sh', st.st_mode | stat.S_IEXEC)

        subprocess.call(['sh', "dashingShell.sh"])

#endregion

#region functions outside the class

def getRequiredFiles():
    files = [
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/Dashing/dashing_s512",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/Dashing/dashingShell.sh",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/client/Dashing/readHllandWrite.sh",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/Compiled%20Model/client.zip",
        r"https://raw.githubusercontent.com/bjorgkav/concreteml-covid-classifier/main/selected%20features.txt",
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
        #getRequiredFiles()
        pass

    app = ClientTkinterUiDesignApp()
    app.run()
