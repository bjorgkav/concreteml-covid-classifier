#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from concrete.ml.sklearn import LogisticRegression
import time
import pandas as pd

#import the dataset here (GISAID; try downloading individual FASTA files if di talaga kaya idownload yung EPISET)

dataset = pd.read_csv("formatted GISAID (04-17-2023).csv")
dataset.head()

#remove "EPI_ISL_" from ID
new_ID_col = []
for i in range(0, len(dataset['Accession ID'])):
    new_ID_col.append(dataset['Accession ID'].loc[i].replace("EPI_ISL_", ""))
dataset['Accession ID'] = new_ID_col

feature_cols = [c for c in dataset.columns[2:]]

x = dataset[feature_cols] #must be floats
y = dataset['Lineage'] #must be integers

# Preprocessing with labels for the lineage
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

x = x.astype(float)

print(x)
print(y)


# In[87]:


# Retrieve train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=10
)

# Initialize model and fix the number of bits to used for quantization 
model = LogisticRegression(n_bits=8)

# Fit the model
model.fit(X_train, y_train)

# Run the predictions on non-encrypted data as a reference
y_pred_clear = model.predict(X_test, execute_in_fhe = False)

# Output (plaintext vs FHE):
print("In clear:  ", le.inverse_transform(y_pred_clear))
print("Accuracy rate:  ", accuracy_score(y_test, y_pred_clear) * 100, "%")


#low/higly volatile accuracy may be attributed to small dataset and too many features 
#(feature selection needed and more samples are required)
print(y_pred_clear)
print(y_test) 



# In[86]:


# Compile into a FHE model
model.compile(x)

# Run the inference in FHE
y_pred_fhe = model.predict(X_test, execute_in_fhe=True)

print("In FHE    :", y_pred_fhe)
print(f"Comparison: {int((y_pred_fhe == y_pred_clear).sum()/len(y_pred_fhe)*100)}% similar")


# In[ ]:




