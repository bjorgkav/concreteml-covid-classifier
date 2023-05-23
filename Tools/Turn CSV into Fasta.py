import pandas as pd
import os
path = "FASTAfiles"

df = pd.read_csv("Upsampling_B.1.617.2_B.1.1.529.csv")
deletion_list = []

isExist = os.path.exists(path)
if not isExist:
    os.makedirs(path)
    print(f"Directory {path} was created since it did not exist.")

for i in range(0, len(df['Sequence'])):
    if(len(df.loc[i]['Sequence'][20000:])>0):
        #filename = (f"{df.loc[i]['Accession ID']}.fasta".replace("EPI_ISL_", ''))
        #f = open(f"./FASTAFiles/{filename}", "w")
        #f.write(df.loc[i]['Sequence'][20000:]) #don't forget to truncate!
        #f.close()
        print('')
    else:
        deletion_list.append(df.loc[i]['Accession ID'])
        #print(f"Invalid FASTA sequence found: {df.loc[i]['Accession ID']}")

for item in deletion_list:
    print(item)
#print(len(list))

#df.to_csv("ADJUSTED DATASET (05-04-2023).csv",header=True,index=False)