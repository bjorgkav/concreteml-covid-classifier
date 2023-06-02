#!/usr/bin/python3
import tkinter as tk
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkLabel,
    CTkTextbox,
    set_appearance_mode,
    set_default_color_theme)


class ClientTkinterUiDesignApp:
    def __init__(self, master=None):
        # build ui
        self.root = CTk(None)
        self.root.configure(padx=60, pady=10)
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        self.root.title(
            "FHE-Enabled SARS-CoV-2 Classifier System (Client-side)")
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
        self.dashing_name_var = tk.StringVar()
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

    def getDashingInput(self):
        pass

    def processData(self):
        pass


if __name__ == "__main__":
    app = ClientTkinterUiDesignApp()
    app.run()
