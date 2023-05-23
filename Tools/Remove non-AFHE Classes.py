import pandas as pd

df = pd.read_csv("DATASET (05-04-2023).csv")
#B.1.617.2 (Delta), C.37 (Lambda), B.1.621 (Mu) and B.1.1.529 (Omicron)
best_classes = ['B.1.617.2','B.1.621','C.37','B.1.1.529']
new_df = df[df.Lineage.isin(best_classes)]

print(new_df['Lineage'].value_counts())
print(f'\nTotal values: {new_df["Lineage"].value_counts().sum()}')

new_df.to_csv("AFHE DATASET (05-04-2023).csv",header=True,index=False)