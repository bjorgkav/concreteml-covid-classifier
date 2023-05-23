# Python function to convert .tsv file to .csv file
import os
import re
import datetime as dt

def TSVtoCSV(filename = r"(sequencing) gisaid_hcov-19_2023_03_23_04.tsv", outputfile = rf"GISAID metadata {dt.datetime.today().strftime(r'%m-%d-%Y')}.csv"): 
  file_dir = os.path.dirname(filename)
  # reading given tsv file
  with open(filename, 'r') as myfile: 
    with open(f"{file_dir}/{outputfile}", 'w') as csv_file:
      for line in myfile:
        
        # Replace every tab with comma
        fileContent = re.sub("\t", ",", line)
        
        # Writing into csv file
        csv_file.write(fileContent)
  
  # output
  print(f"Successfully written Metadata CSV file to {outputfile}")
  return outputfile

def parseLines(fasta_file, new_file):
  count = 0
  last_line_fasta = False
  seq_str = ""
  for line in fasta_file.readlines():
    line_str = ""
    #is a sequence ID line
    if ">" in line:
        if last_line_fasta == True: 
            print(f'Length of seq_str: {len(seq_str[20000:])}')
            new_file.write(f"{seq_str[20000:]}\n")
            seq_str = ""
            last_line_fasta = False

        count += 1
        print(f"New specimen found. Count: {count}")

        #start new row
        id = line.split("|")[1].strip()
        line_str = f"{id},"
        
        new_file.write(f"{line_str}")

    #is a sequence line, remove first 20kb
    else:
        last_line_fasta = True
        seq_str += f"{line.strip()}"
  new_file.write(f"{seq_str[20000:]}\n")

def makeFASTACSV(filename = r"(fasta) gisaid_hcov-19_2023_03_16_06.fasta", outputfile = rf"GISAID fasta data {dt.datetime.today().strftime(r'%m-%d-%Y')}.csv"):
  file_dir = os.path.dirname(filename)
  with open(filename, "r") as fasta_file:
    with open(f"{file_dir}/{outputfile}", "w") as new_file:
      new_file.write("Accession ID,Sequence\n")
      parseLines(fasta_file, new_file)

  print(f"New FASTA CSV file written to name: {outputfile}")
      
  fasta_file.close()
  new_file.close()

  return outputfile