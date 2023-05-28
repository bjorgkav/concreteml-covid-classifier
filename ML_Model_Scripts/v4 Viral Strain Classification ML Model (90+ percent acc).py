#!/usr/bin/env python
# coding: utf-8

# In[19]:


from numpy import mean
from numpy import std
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score, roc_auc_score
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

#select set option
set = -1

#import the dataset here (GISAID; try downloading individual FASTA files if di talaga kaya idownload yung EPISET)
#if(set == -1):
#    dataset_name = "AFHE DATASET (05-04-2023).csv"
#elif(set == 0):
#    dataset_name = "ADJUSTED DATASET (05-04-2023).csv"
#else:
#    dataset_name = "ADJUSTED DOWNSIZED DATASET (05-04-2023).csv"
#dataset = pd.read_csv(dataset_name)

dataset = pd.read_csv("AFHE DATASET (05-18-2023).csv")

#print(dataset['Lineage'].value_counts())

#remove "EPI_ISL_" from ID
#new_ID_col = []
#for i in range(0, len(dataset['Accession ID'])):
#    new_ID_col.append(str(dataset['Accession ID'].loc[i].replace("EPI_ISL_", "")))
#dataset['Accession ID'] = new_ID_col

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

print("Shape of x: ", x.shape)
print("Shape of y:", y.shape)

#print(dataset)


# In[20]:


# Feature Selection Cell (ensemble attempted)

x = feature_selection(x, "var", var_percent = 0.80)
x = feature_selection(x, "kbest", n_features = 15)
#x = feature_selection(x, "pca", n_features = 5)


# In[21]:


# Retrieve train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=.25) #stratify=y

st_x = StandardScaler()
X_train = st_x.fit_transform(X_train)
X_test = st_x.transform(X_test)


# In[22]:


# Initialize SKLearn model

skmodel = skLR(C=1)
skmodel.fit(X_train,y_train)
skmodel.predict(X_test)
print("Accuracy for sklearn: ", skmodel.score(X_test,y_test)*100,"%")


# In[23]:


# Initialize model and fix the number of bits to used for quantization 
model = LogisticRegression(C=1)

# Fit the model
model.fit(X_train, y_train)

# Run the predictions on non-encrypted data as a reference
y_pred_clear = model.predict(X_test, execute_in_fhe = False)

# Output (plaintext vs FHE):
# print("In clear:  ", le.inverse_transform(y_pred_clear))
# accuracy_score(y_test, y_pred_clear)
print("Accuracy rate for quantized plaintext:  ", model.score(X_test,y_test) * 100, "%")

#low/higly volatile accuracy may be attributed to small dataset and too many features 
#(feature selection needed and more samples are required)
print("PREDICTION:\n", y_pred_clear)
print("ACTUAL:\n", y_test) 

# Compile into a FHE model
model.compile(x)
print("model compiled!")

# Run the inference in FHE
#y_pred_fhe = model.predict(X_test, execute_in_fhe=True)
#print("Accuracy rate for quantized plaintext:  ", accuracy_score(y_test, y_pred_fhe) * 100, "%")

#print("In FHE    :", y_pred_fhe)
#print(f"Comparison: {int((y_pred_fhe == y_pred_clear).sum()/len(y_pred_fhe)*100)}% similar")


# In[24]:


#Get AUC for multiclass
#NOTE WE HAVE A MULTICLASS BUT NOT MULTILABEL PROBLEM. only one label selected from multiple classes is assigned

print("Scikit learn AUROC (One vs Rest): ", roc_auc_score(y, skmodel.predict_proba(x), multi_class='ovr'))
print("Scikit learn AUROC (One vs One): ", roc_auc_score(y, skmodel.predict_proba(x), multi_class='ovo'))

print("Concrete-ML AUROC (One vs Rest): ", roc_auc_score(y, model.predict_proba(x), multi_class='ovr'))
print("Concrete-ML AUROC (One vs One): ", roc_auc_score(y, model.predict_proba(x), multi_class='ovo'))


# In[7]:


from concrete.ml.sklearn.svm import LinearSVC
from sklearn.svm import LinearSVC as skSVC
from concrete.ml.sklearn.rf import RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier as skRF

#SKLEARN LINEAR REGRESSION
skmodel2 = skLinear()
skmodel2.fit(X_train,y_train)
skmodel2.predict(X_test)
print("Sklearn Linear Regression Accuracy: ", skmodel2.score(X_test,y_test)*100,"%")

model2 = LinearRegression()
model2.fit(X_train,y_train)
model2.predict(X_test)
print("Concrete-ML Linear Regression Accuracy: ", model2.score(X_test,y_test)*100,"%")

#SKLEARN RANDOM FOREST
skmodel3 = skRF()
skmodel3.fit(X_train, y_train)
skmodel3.predict(X_test)
print("Sklearn Random Forest Accuracy: ",skmodel3.score(X_test,y_test)*100,"%")

model3 = RandomForestClassifier()
model3.fit(X_train, y_train)
model3.predict(X_test)
print("Concrete-ML Random Forest Accuracy: ",model3.score(X_test,y_test)*100,"%")

#SKLEARN SVC
skmodel4 = skSVC()
skmodel4.fit(X_train, y_train)
skmodel4.predict(X_test)
print("Sklearn SVC Accuracy: ",skmodel4.score(X_test,y_test)*100,"%")

model4 = LinearSVC()
model4.fit(X_train, y_train)
model4.predict(X_test)
print("Concrete-ML SVC Accuracy: ",model4.score(X_test,y_test)*100,"%")


# In[ ]:


# prepare the cross-validation procedure
cv = RepeatedKFold(n_splits=10, n_repeats=3)

# evaluate model
scores = cross_val_score(model, x, y, scoring='accuracy', cv=cv, n_jobs=-1)

# report performance
print('Accuracy: %.3f (%.3f)' % (mean(scores), std(scores)))


# In[ ]:




