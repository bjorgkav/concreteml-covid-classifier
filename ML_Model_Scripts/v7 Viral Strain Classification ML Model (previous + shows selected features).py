#!/usr/bin/env python
# coding: utf-8

# In[44]:


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

start_time = time.time()

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
        #cols_idxs = sel.get_support(indices=True)
    elif opt == "kbest":
        print("\nUsing K best features feature selection...")
        print("Shape of x before selection: ", x.shape)
        selector = SelectKBest(chi2, k=n_features)
        x = selector.fit_transform(x, y)
        
        #cols_idxs = selector.get_support(indices=True)
        
        print("Shape of x after selection: ", x.shape)
    elif opt == "pca":
        print("\nUsing PCA feature selection...")
        x_scaled = StandardScaler().fit_transform(x)
        pca = PCA(n_components=n_features)
        pca_features = pca.fit_transform(x_scaled)
        print('Shape before PCA: ', x_scaled.shape)
        print('Shape after PCA: ', pca_features.shape)
        x = pca_features
        #cols_idxs = pca.get_support(indices=True)
    else:
        print("")
    return x#, cols_idxs

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

x = dataset.loc[:,feature_cols] #must be floats
y = dataset.loc[:,'Lineage'].values #must be integers

#print(x)
#print(y)

# Preprocessing with labels for the lineage
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

x = x.astype(float)

#print(x)

print("Shape of x: ", x.shape)
print("Shape of y:", y.shape)

#print(dataset)

print(f"Running time is {time.time() - start_time} seconds")


# In[45]:


# Feature Selection Cell (ensemble attempted)
start_time = time.time()

#x, cols_idxs = feature_selection(x, dataset, "var", var_percent = 0.80)
x = feature_selection(x, "kbest", n_features = 20) #col_idxs
#x = feature_selection(x, "pca", n_features = 5)

print(x)
#print(dataset.iloc[:,cols_idxs])

# print("\nSelected features: ")
# for col in cols_idxs:
#     print(feature_cols[col])

print(f"Running time is {time.time() - start_time} seconds")


# In[15]:


# Retrieve train and test sets

start_time = time.time()

#X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=.20) #for faster inference

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=.40)

# st_x = StandardScaler()
# X_train = st_x.fit_transform(X_train)
# X_test = st_x.transform(X_test)

print(f"Running time is {time.time() - start_time} seconds")


# In[16]:


# Initialize SKLearn model
start_time = time.time()

skmodel = skLR(C=1)
skmodel.fit(X_train,y_train)
y_pred_sklearn = skmodel.predict(X_test)
print("Accuracy for sklearn against test set: ", skmodel.score(X_test,y_test)*100,"%")

print(f"Running time is {time.time() - start_time} seconds")


# In[17]:


# Initialize model and fix the number of bits to used for quantization 
model = LogisticRegression(C=1)

# Fit the model
model.fit(X_train, y_train)

start_time = time.time()
# Run the predictions on non-encrypted data as a reference
#y_pred_clear = model.predict(X_test, execute_in_fhe = False)
y_pred_clear = model.predict(X_test)
#y_pred_clear = model.predict(X_test)

# Output (plaintext vs FHE):
# print("In clear:  ", le.inverse_transform(y_pred_clear))
# accuracy_score(y_test, y_pred_clear)
print("Accuracy rate for quantized plaintext:  ", model.score(X_test,y_test) * 100, "%")

#low/higly volatile accuracy may be attributed to small dataset and too many features 
#(feature selection needed and more samples are required)
#print("PREDICTION:\n", y_pred_clear)
#print("ACTUAL:\n", y_test) 
print(f"Running time for plaintext training and test inference is {time.time() - start_time} seconds")

start_time = time.time()
print("Compiling...")
# Compile into a FHE model
model.compile(x)
print("model compiled!")
print(f"Running time for compilation is {time.time() - start_time} seconds")

# Run the inference in FHE

#start_time = time.time()
#print("Beginning FHE inference....")

#y_pred_fhe = model.predict(X_test, execute_in_fhe=True)
y_pred_fhe = model.predict(X_test, fhe = "execute")
print("Accuracy rate for quantized ciphertext (FHE):  ", accuracy_score(y_test, y_pred_fhe) * 100, "%")

#print("In FHE    :", y_pred_fhe)
print(f"Comparison: {int((y_pred_fhe == y_pred_clear).sum()/len(y_pred_fhe)*100)}% similar")

print(f"Running time for FHE inference is {time.time() - start_time} seconds")


# In[18]:


#Get AUC for multiclass
#NOTE WE HAVE A MULTICLASS BUT NOT MULTILABEL PROBLEM. only one label selected from multiple classes is assigned
print("***** USING AUROC ON BOTH TRAINING AND TESTING SETS TO CHECK FOR OVERFITTING AND GENERAL PEROFRMANCE *****")
print("***** Note: If training AUROC is high but testing AUROC is low, the model is overfitted. *****\n")

print("Against the training set...")

print("Scikit learn AUROC (One vs Rest): ", roc_auc_score(y_train, skmodel.predict_proba(X_train), multi_class='ovr'))
print("Scikit learn AUROC (One vs One): ", roc_auc_score(y_train, skmodel.predict_proba(X_train), multi_class='ovo'))

print("Concrete-ML AUROC (One vs Rest): ", roc_auc_score(y_train, model.predict_proba(X_train), multi_class='ovr'))
print("Concrete-ML AUROC (One vs One): ", roc_auc_score(y_train, model.predict_proba(X_train), multi_class='ovo'))

print("\nAgainst the testing set...")

print("Scikit learn AUROC (One vs Rest): ", roc_auc_score(y_test, skmodel.predict_proba(X_test), multi_class='ovr'))
print("Scikit learn AUROC (One vs One): ", roc_auc_score(y_test, skmodel.predict_proba(X_test), multi_class='ovo'))

print("Concrete-ML Plaintext AUROC (One vs Rest): ", roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovr'))
print("Concrete-ML Plaintext AUROC (One vs One): ", roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovo'))

#print("Concrete-ML FHE AUROC (One vs Rest): ", roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovr'))
#print("Concrete-ML FHE AUROC (One vs One): ", roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovo'))


# In[10]:


from sklearn.metrics import confusion_matrix
print("***Note: The diagonal elements are the correctly predicted samples. ***")

print("Confusion matrix for SKLearn Plaintext: ")
print(confusion_matrix(y_test, y_pred_sklearn), "\n")

print("Confusion matrix for Quantized Plaintext: ")
print(confusion_matrix(y_test, y_pred_clear), "\n")

#print("Confusion matrix for FHE: ")
#print(confusion_matrix(y_test, y_pred_fhe))


# In[10]:


#Attempting to save the model
# from concrete.ml.deployment import FHEModelClient, FHEModelDev, FHEModelServer

# start_time = time.time()

# fhemodel_dev = FHEModelDev("./concrete-covid-classifier", model)
# fhemodel_dev.save()

# print(f"Running time for saving the FHE model is {time.time() - start_time} seconds")


# In[6]:


# #Saving Scikit-learn model
# from joblib import dump, load

# dump(skmodel, 'concrete-covid-classifier/scikitlearnmodel.joblib')
#loaded_model = load('scikitlearnmodel.joblib')


# In[ ]:


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


# #ALTERNATE CROSS-VALIDATION METHOD (K-fold Cross validation)
# from sklearn.model_selection import KFold
# k = 5
# k_fold = KFold(n_splits = k, random_state = None)

# sklmodelcross = skLR()

# acc_scores = []

# for training_index, testing_index in k_fold.split(x):
#     X_train, X_test = x[training_index,:], x[testing_index,:]  
#     y_train, y_test = y[training_index] , y[testing_index]
#     sklmodelcross.fit(X_train,y_train)
#     y_pred = sklmodelcross.predict(X_test)
#     acc = accuracy_score(y_pred , y_test)  
#     acc_scores.append(acc)

# mean_acc_score = sum(acc_scores) / k

# print("Accuracy score of each fold (sklearn plaintext): ", acc_scores)  
# print("Mean accuracy score (sklearn plaintext): ", mean_acc_score)  


# In[ ]:


# #ALTERNATE CROSS-VALIDATION METHOD (K-fold Cross validation)
# from sklearn.model_selection import KFold
# k = 100
# k_fold = KFold(n_splits = k, random_state = None)

# concreteLRcross = LogisticRegression()

# acc_scores = []

# for training_index, testing_index in k_fold.split(x):
#     X_train, X_test = x[training_index,:], x[testing_index,:]  
#     y_train, y_test = y[training_index] , y[testing_index]
#     concreteLRcross.fit(X_train,y_train)
#     y_pred = concreteLRcross.predict(X_test)
#     acc = accuracy_score(y_pred , y_test)  
#     acc_scores.append(acc)

# mean_acc_score = sum(acc_scores) / k

# print("Accuracy score of each fold (quantized plaintext): ", acc_scores)  
# print("Mean accuracy score (quantized plaintext): ", mean_acc_score)  

