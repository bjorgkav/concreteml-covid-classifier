import pandas as pd

df = pd.read_csv("DATASET (05-18-2023).csv")
big_classes = ['B.1.617.2','B.1.621','B.1.621.2','BA.1','BA.1.1','BA.1.15','BA.1.17','BA.1.17.2','C.37']

new_df = df[df.Lineage.isin(big_classes)]

print(new_df['Lineage'].value_counts())
print(f'\nTotal values: {new_df["Lineage"].value_counts().sum()}')

new_df.to_csv("AFHE DATASET (05-18-2023).csv",header=True,index=False)