# %%
from numpy import mean
from numpy import std
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score, roc_auc_score, recall_score, confusion_matrix, ConfusionMatrixDisplay
from concrete.ml.sklearn import LogisticRegression, LinearRegression
from concrete.ml.sklearn.svm import LinearSVC
from sklearn.svm import LinearSVC as skSVC
from concrete.ml.sklearn.rf import RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier as skRF
from sklearn.linear_model import LogisticRegression as skLR
from sklearn.linear_model import LinearRegression as skLinear
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import time, numpy
import pandas as pd

start_time = time.time()

dataset = pd.read_csv("AFHE DATASET (05-18-2023).csv")

feature_cols = [c for c in dataset.columns[2:]]

x = dataset.loc[:,feature_cols].values #must be floats
y = dataset.loc[:,'Lineage'].values #must be integers

# Preprocessing with labels for the lineage
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)
print(le.classes_)

x = x.astype(float)

print("Shape of x: ", x.shape)
print("Shape of y:", y.shape)

print(f"Running time is {time.time() - start_time} seconds")

# %%
# Feature Selection

start_time = time.time()

print("\nUsing K best features feature selection...")
print("Shape of x before selection: ", x.shape)
selector = SelectKBest(chi2, k=20)
x = selector.fit_transform(x, y)
col_idxs = selector.get_support(indices=True)
print("Shape of x after selection: ", x.shape)

print(f"Running time is {time.time() - start_time} seconds")

# %%
# Retrieve train and test sets
start_time = time.time()
X_train, X_test, y_train, y_test = train_test_split(
x, y, test_size=.20)
print(f"Test set size: {X_test.shape}")
print(f"Running time is {time.time() - start_time} seconds")

# %%
#NOTE WE HAVE A MULTICLASS BUT NOT MULTILABEL PROBLEM. only one label selected from multiple classes is assigned
print("Getting metrics for scikit-learn model (Plaintext)...")
skmodel = skLR(C=1)

start_time = time.time()
skmodel.fit(X_train,y_train)
print(f"Training time is {time.time() - start_time} seconds")

start_time = time.time()
y_pred_sklearn = skmodel.predict(X_test)
print(f"Prediction time is {time.time() - start_time} seconds")
print(f"Accuracy: {skmodel.score(X_test,y_test)*100}%")
print(f"Macro-averaged ROC AUC Score: {roc_auc_score(y, skmodel.predict_proba(x), multi_class='ovr')}")
print(f"Recall: {recall_score(y_test, y_pred_sklearn, average='weighted')*100}%")
sklearn_cm_display = ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred_sklearn), display_labels=le.classes_)
sklearn_cm_display.plot()
plt.show()

# %%
print("Getting metrics for Concrete-ML model (Quantized Plaintext)...")
model = LogisticRegression(C=1)

# Fit the model
start_time = time.time()
model.fit(X_train, y_train)
print(f"Training time is {time.time() - start_time} seconds")

# Run the predictions on non-encrypted data as a reference
start_time = time.time()
y_pred_clear = model.predict(X_test)
print(f"Prediction time is {time.time() - start_time} seconds")
print(f"Accuracy: {model.score(X_test,y_test) * 100}%")
print(f"Macro-averaged ROC AUC Score: {roc_auc_score(y, model.predict_proba(x), multi_class='ovr')}")
print(f"Recall: {recall_score(y_test, y_pred_clear, average='weighted')*100}%")
concrete_plain_display = ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred_clear), display_labels=le.classes_)
concrete_plain_display.plot()
plt.show()

#%%
print("Getting metrics for Concrete-ML model (FHE)...")

start_time = time.time()
print("Compiling the quantized model...")
model.compile(x)
print("Model compiled!")
print(f"Compilation time is {time.time() - start_time} seconds")

start_time = time.time()
y_pred_fhe = model.predict(X_test, fhe="execute")
print(f"Prediction time is {time.time() - start_time} seconds")
print(f"Accuracy: {accuracy_score(y_test, y_pred_fhe) * 100}%")
print(f"Macro-averaged ROC AUC Score: {roc_auc_score(y, model.predict_proba(x), multi_class='ovr')}")
print(f"Recall: {recall_score(y_test, y_pred_fhe, average='weighted')*100}%")
print(f"Comparison (FHE vs Plaintext): {int((y_pred_fhe == y_pred_sklearn).sum()/len(y_pred_fhe)*100)}% similar")
print(f"Comparison (FHE vs Quantized Plaintext): {int((y_pred_fhe == y_pred_clear).sum()/len(y_pred_fhe)*100)}% similar")
concrete_fhe_display = ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred_fhe), display_labels=le.classes_)
concrete_fhe_display.plot()
plt.show()

# %%
print(f"Sklearn Accuracy (Linear Reg, RF, SVC):")

#SKLEARN LINEAR REGRESSION
skmodel2 = skLinear()
skmodel2.fit(X_train,y_train)
skmodel2.predict(X_test)
print("Sklearn Linear Regression Accuracy: ", skmodel2.score(X_test,y_test)*100,"%")

#SKLEARN RANDOM FOREST
skmodel3 = skRF()
skmodel3.fit(X_train, y_train)
skmodel3.predict(X_test)
print("Sklearn Random Forest Accuracy: ",skmodel3.score(X_test,y_test)*100,"%")

#SKLEARN SVC
skmodel4 = skSVC()
skmodel4.fit(X_train, y_train)
skmodel4.predict(X_test)
print("Sklearn SVC Accuracy: ",skmodel4.score(X_test,y_test)*100,"%")

print(f"\nConcrete-ML Accuracy (Linear Reg, RF, SVC):")

model2 = LinearRegression()
model2.fit(X_train,y_train)
model2.predict(X_test)
print("Concrete-ML Linear Regression Accuracy: ", model2.score(X_test,y_test)*100,"%")

model3 = RandomForestClassifier()
model3.fit(X_train, y_train)
model3.predict(X_test)
print("Concrete-ML Random Forest Accuracy: ",model3.score(X_test,y_test)*100,"%")

model4 = LinearSVC()
model4.fit(X_train, y_train)
model4.predict(X_test)
print("Concrete-ML SVC Accuracy: ",model4.score(X_test,y_test)*100,"%")

model2.compile(x)
model3.compile(x)
model4.compile(x)
model2.predict(X_test)
model3.predict(X_test)
model4.predict(X_test)

print("\nFHE Concrete-ML Linear Regression Accuracy: ", model2.score(X_test,y_test)*100,"%")
print("FHE Concrete-ML Random Forest Accuracy: ",model3.score(X_test,y_test)*100,"%")
print("FHE Concrete-ML SVC Accuracy: ",model4.score(X_test,y_test)*100,"%")

# %%
import json

#Attempting to save the model
from concrete.ml.deployment import FHEModelClient, FHEModelDev, FHEModelServer

start_time = time.time()
fhemodel_dev = FHEModelDev("./concrete-covid-classifier", model)
fhemodel_dev.save()
print(f"Running time for saving the FHE model is {time.time() - start_time} seconds")

for col in col_idxs:
    print(feature_cols[col])

for c in le.classes_:
    print(c)

start_time = time.time()
with open("features_and_classes.txt", "w") as f:
    classes_list = list(le.classes_)
    temp_dict = {"features":[feature_cols[col] for col in col_idxs], "classes":{classes_list.index(x):x for x in classes_list}}

    f.write(json.dumps(temp_dict))
print(f"Running time for saving the features and classes is {time.time() - start_time} seconds")