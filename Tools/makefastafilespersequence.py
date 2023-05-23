#make fasta files per sequence
import datetime as dt
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def makeFASTAPerLine(filename = r"(fasta) gisaid_hcov-19_2023_03_16_06.fasta", folder = "FASTAfiles"):
  file_dir = os.path.join(os.path.dirname(filename), folder)
  os.mkdir(file_dir)
  try:
    with open(filename, "r") as source_file:
        last_line_fasta = False
        seq_str = ""
        for line in source_file.readlines():
            count = 0
            print(f"Line {count}")
            name = ""
            #is a sequence ID line
            if ">" in line:
                if last_line_fasta:
                    f.write(f"{seq_str[20000:]}")
                    f.close()
                    last_line_fasta = False
                    seq_str = ""

                #store ID for filename
                name = line.split("|")[1].strip().replace('EPI_ISL_', '')
                f = open(f"{file_dir}/{name}.fasta", "w")
                f.write(f"{line}")

            #is a sequence line, remove first 20kb
            else:
                last_line_fasta = True
                seq_str += f"{line.strip()}"
                #f.write(f"{line}")
        f.write(f"{seq_str[20000:]}")
        f.close()
  except Exception as e:
    print(f"Error! {e}")

name = askopenfilename()
makeFASTAPerLine(filename=name)