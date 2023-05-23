#!/usr/bin/env python
# coding: utf-8

# In[3]:


from numpy import mean
from numpy import std
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from concrete.ml.sklearn import LogisticRegression, LinearRegression
from sklearn.linear_model import LogisticRegression as skLR
from sklearn.linear_model import LinearRegression as skLinear
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import time
import pandas as pd

def feature_selection(x, opt = "", var_percent = 0.8, n_features = 30):
    if opt == "var":
        print("\nUsing variance threshold feature selection...")
        # Remove all features that have low variance in more than (percent)% of the samples.
        #percent = .80
        sel = VarianceThreshold(threshold=(var_percent * (1 - var_percent)))
        print("Shape of X: ", x.shape)
        #print(x.iloc[0])
        x = sel.fit_transform(x)
        print("After feature selection: ", len(x[0]), " features")
        #print(x[0])
    elif opt == "kbest":
        print("\nUsing K best features feature selection...")
        print("Shape of x before selection: ", x.shape)
        x = SelectKBest(chi2, k=n_features).fit_transform(x, y)
        print("Shape of x after selection: ", x.shape)
    elif opt == "pca":
        print("\nUsing PCA feature selection...")
        x_scaled = StandardScaler().fit_transform(x)
        pca = PCA(n_components=n_features)
        pca_features = pca.fit_transform(x_scaled)
        print('Shape before PCA: ', x_scaled.shape)
        print('Shape after PCA: ', pca_features.shape)
        x = pca_features
    else:
        print("")
    return x

#import the dataset here (GISAID; try downloading individual FASTA files if di talaga kaya idownload yung EPISET)

dataset = pd.read_csv("DATASET (05-04-2023).csv")
dataset.head()

#remove "EPI_ISL_" from ID
new_ID_col = []
for i in range(0, len(dataset['Accession ID'])):
    new_ID_col.append(str(dataset['Accession ID'].loc[i].replace("EPI_ISL_", "")))
dataset['Accession ID'] = new_ID_col

feature_cols = [c for c in dataset.columns[2:]]
#print(feature_cols)

x = dataset.loc[:,feature_cols].values #must be floats
y = dataset.loc[:,'Lineage'].values #must be integers

#print(x)
#print(y)

# Preprocessing with labels for the lineage
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

x = x.astype(float)

print("done!", x.shape)

#print(dataset)


# In[4]:


# Feature Selection Cell (ensemble attempted)

x = feature_selection(x, "var", var_percent = 0.80)
#x = feature_selection(x, "pca", n_features = 30)


# In[5]:


# Retrieve train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.10, random_state = 42) #stratify=y

st_x = StandardScaler()
X_train = st_x.fit_transform(X_train)
X_test = st_x.transform(X_test)


# In[6]:


# Initialize SKLearn model

skmodel = skLR(C=0.5)
skmodel.fit(X_train,y_train)
skmodel.predict(X_test)
print(skmodel.score(X_test,y_test)*100,"%")


# In[7]:


# Initialize model and fix the number of bits to used for quantization 
model = LogisticRegression(C=0.2)

# Fit the model
model.fit(X_train, y_train)

# Run the predictions on non-encrypted data as a reference
y_pred_clear = model.predict(X_test, execute_in_fhe = False)

# Output (plaintext vs FHE):
#print("In clear:  ", le.inverse_transform(y_pred_clear))
#print("Accuracy rate:  ", accuracy_score(y_test, y_pred_clear) * 100, "%")
print(model.score(X_test, y_test)*100,"%")

#low/higly volatile accuracy may be attributed to small dataset and too many features 
#(feature selection needed and more samples are required)
#print("PREDICTION:\n", y_pred_clear)
#print("ACTUAL:\n", y_test) 

# Compile into a FHE model
model.compile(x)
print("model compiled!")

# Run the inference in FHE
#y_pred_fhe = model.predict(X_test, execute_in_fhe=True)

#print("In FHE    :", y_pred_fhe)
#print(f"Comparison: {int((y_pred_fhe == y_pred_clear).sum()/len(y_pred_fhe)*100)}% similar")


# In[8]:


skmodel2 = skLinear()
skmodel2.fit(X_train,y_train)
skmodel2.predict(X_test)
print(skmodel2.score(X_test,y_test)*100,"%")

model2 = LinearRegression()
model2.fit(X_train,y_train)
model2.predict(X_test)
print(model2.score(X_test,y_test)*100,"%")


# In[ ]:


# prepare the cross-validation procedure
cv = RepeatedKFold(n_splits=10, n_repeats=3)

# evaluate model
scores = cross_val_score(model, x, y, scoring='accuracy', cv=cv, n_jobs=-1)

# report performance
print('Accuracy: %.3f (%.3f)' % (mean(scores), std(scores)))


# In[ ]:


# AUC for metrics
from sklearn import metrics
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_clear)
metrics.auc(fpr, tpr)


# In[ ]:




