#Developed by Johann Vivas on 03/24/2023

import os
from pandas import read_csv, DataFrame, merge
import datetime as dt
from warnings import filterwarnings
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from formatCSV import makeFASTACSV, TSVtoCSV

filterwarnings('ignore', category=UserWarning, module="openpyxl")

def combine(metadf, fastadf):
    try:
        new_df = fastadf.copy().join(metadf["Lineage"]) #Accession ID, Sequence, Lineage, Clade
        new_df.drop(columns=['Sequence'])
        new_headers = ['Accession ID', 'Lineage']
        new_df = new_df.reindex(columns=new_headers)
        return new_df

    except Exception as e:
        print(e)

def get2Filenames(option):
    first_file_desc = "Metadata table" if option == 1 else "Formatted GISAID Data"
    second_file_desc = "FASTA sequence table" if option == 1 else "Dashing Features CSV"

    print(f"Please select your {first_file_desc}.")
    Tk().withdraw()
    first_file = askopenfilename()

    print(f"Please select your {second_file_desc}.")
    Tk().withdraw()
    second_file = askopenfilename()

    return first_file, second_file

def formatMetaFasta(meta_file, fasta_file):

    file_dir = os.path.dirname(meta_file)
    meta_csv = TSVtoCSV(meta_file)

    meta_df = read_csv(f"{file_dir}/{meta_csv}")[['Accession ID', 'Lineage']].copy()

    fasta_csv = makeFASTACSV(fasta_file)

    formatted_df = combine(meta_df, read_csv(f"{file_dir}/{fasta_csv}"))
    formatted_name = fr'{file_dir}/formatted GISAID ({dt.datetime.today().strftime(r"%m-%d-%Y")}).csv'

    try:
        print(f"Final formatted CSV written to name: {formatted_name}.")
        formatted_df.to_csv(formatted_name, index = False, header = True)
    except Exception as e:
        print(f"Error: {e}")

def combineGISAIDDashing(gisaiddf, dashingdf, file_dir):
    try:
        new_df = merge(gisaiddf.copy(), dashingdf, on="Accession ID")
        final_dataset_name = fr'{file_dir}/DATASET ({dt.datetime.today().strftime(r"%m-%d-%Y")}).csv'
        new_df.to_csv(final_dataset_name, index = False, header = True)
        print(f"Combined Dataset (GISAID and Features from Dashing) was saved to {final_dataset_name}.")
    except Exception as e:
        print(f"Error: {e}")

def parseChoice(value):
    match value:
        case 1:
            meta_file, fasta_file = get2Filenames(value)
            formatMetaFasta(meta_file, fasta_file)
            
            #print("This function is no longer required. Refer to the workflow to see what to do for the creation of the dataset.")
        case 2:
            #ask for formatted gisaid and dashing output csv, combine
            formatted_gisaid, dashing_csv = get2Filenames(value)
            file_dir = os.path.dirname(formatted_gisaid)
            combineGISAIDDashing(read_csv(formatted_gisaid), read_csv(dashing_csv), file_dir)
        case 3:
            print("Thank you for using the tool.")

menu_length = 53
title = "DATASET FORMATTING TOOL"
half_line, full_line = '='*((menu_length-len(title))//2), '='*menu_length

menu_str = "1.Combine GISAID metadata and FASTA files\n2.Add Dashing output to formatted GISAID\n3.Exit\n\n"

print(f"{half_line}{title}{half_line}")
print(menu_str)
choices = [1,2,3]
response = -1

while (response != choices[-1]):
    if response != -1: print("\nReturning to menu...\n")
    print(menu_str)
    response = int(input("Provide input: "))
    parseChoice(response)

print(full_line)
