# -*- coding: utf-8 -*-
"""MLPharmaProjectV2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1itjqDFH09waUPIcCcsw9r09B_t7qhSFW

# Git clone and Instillations
"""

#Clone iFeature repository in order to be able to run feature extraction code

! git clone https://github.com/Superzchen/iFeature

!git clone https://github.com/jwmng/extratrees.git

!pip3 install joblib

#Install biopython in order to be able to parse in sequences from FASTA file format
!pip3 install biopython
!pip3 install tqdm
!pip3 install time
!pip3 install xgboost
!pip3 install seaborn

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

"""# Module Imports"""

#Import necessary modules to run the rest of the code
from tqdm import tqdm
import time
from time import sleep

import xgboost as xgb
import numpy as np
import pandas as pd

import Bio
from Bio import SeqIO
import sklearn
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import balanced_accuracy_score
#from extratrees.src.extratrees import ExtraForest

from sklearn.metrics import roc_curve, auc

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split 
#from sklearn.cross_validation import cross_val_score

import pickle
import tensorflow as tf
import datetime
from tensorflow.keras.callbacks import TensorBoard
import datetime

"""# Functions"""

#Function for plotting ROC curve
def plot_roc_curve(labels, probality, legend_text, auc_tag=True):
    # fpr2, tpr2, thresholds = roc_curve(labels, pred_y)
    fpr, tpr, thresholds = roc_curve(labels, probality)  # probas_[:, 1])
    roc_auc = auc(fpr, tpr)
    if auc_tag:
        rects1 = plt.plot(fpr, tpr, label=legend_text + ' (AUC=%6.3f) ' % roc_auc)
    else:
        rects1 = plt.plot(fpr, tpr, label=legend_text)

"""# Feature Calculation

##Labels Array
"""

#creating labels for the positive and negative sequences
names = []
label = []
sequences = []
fasta_sequences = SeqIO.parse(open('benchmarking.txt'),'fasta')
for fasta in fasta_sequences:
    names.append(fasta.id)
    sequences.append(str(fasta.seq))
    if 'Positive' in fasta.id:
      label.append(1)
    elif 'Negative' in fasta.id:
      label.append(0)

#determing the count for each peptide's sequence length within the data set

alt_sequences = []
seq_len = []
for sequence in sequences:
  #print(len(sequence))
  seq_len.append(len(sequence))
  if len(sequence) > 20:
      sequence = sequence[:20]
  elif len(sequence) <20:
    sequence = sequence.ljust(20, 'X')
  alt_sequences.append(sequence)


print(len(min(alt_sequences, key=len)))
print(len(max(alt_sequences, key=len)))

f = open("alt_benchmarking.txt", "w")

for i in range(len(alt_sequences)):
  f.write(">" + names[i] + "\n" + alt_sequences[i] + "\n")

f.close()


seq_len_arr = []
seq_len_count = []
for i in tqdm(range(11)):
  seq_len_count.append(seq_len.count(i+11))
  seq_len_arr.append(i+11)


plt.bar(seq_len_arr,seq_len_count, color = 'orchid')
plt.xlabel('Sequence Length')
plt.ylabel('Length Count')
plt.title('Sequence Length')

"""## AAC"""

#AAC Feature Extractor
!python iFeature/iFeature.py --file benchmarking.txt --type AAC --out AAC.txt
input_file = "AAC.txt"

file1 = open(input_file, 'r')

Lines = file1.readlines()

id = np.zeros(len(Lines), 'str')
feat_vector = np.zeros(len(Lines), 'str')

i = 0

id = [np.array(line.split()[0]) for line in Lines]

data = {'ID': id}
df_AAC = pd.DataFrame(data)     

for i in range(len(Lines[0].split())-1):
  feat_vect = [np.array(line.split()[i+1]) for line in Lines]
  feat_name = Lines[0].split()[i+1]
  df_AAC[feat_name] = feat_vect


df_AAC['ID'] = id
df_AAC= df_AAC.iloc[1: , :]
df_AAC.head()

"""##  CTDT"""

#CTDC (Composition) feature extraction
!python iFeature/iFeature.py --file benchmarking.txt --type CTDT --out CTDT.txt

input_file2 = "CTDT.txt"

file1 = open(input_file2, 'r')

Lines = file1.readlines()

i = 0

id = [np.array(line.split()[0]) for line in Lines]

data = {'ID': id}
df_CTDT = pd.DataFrame(data)     

for i in tqdm(range(len(Lines[0].split())-1)):
  feat_vect = [np.array(line.split()[i+1]) for line in Lines]
  feat_name = Lines[0].split()[i+1]
  df_CTDT[feat_name] = feat_vect


df_CTDT['ID'] = id   
df_CTDT= df_CTDT.iloc[1: , :]
df_CTDT.head()

"""##DPC"""

#Dipeptide Composition feature extraction
!python iFeature/iFeature.py --file benchmarking.txt --type DPC --out DPC.txt

input_file2 = "DPC.txt"

file1 = open(input_file2, 'r')

Lines = file1.readlines()

id = [np.array(line.split()[0]) for line in Lines]

data = {'ID': id}
df_DPC = pd.DataFrame(data)     

for i in tqdm(range(len(Lines[0].split())-1)):
  feat_vect = [np.array(line.split()[i+1]) for line in Lines]
  feat_name = Lines[0].split()[i+1]
  df_DPC[feat_name] = feat_vect


df_DPC['ID'] = id    
df_DPC= df_DPC.iloc[1: , :]
df_DPC.head()

"""## KSAAP"""

#Composition of K-Spaced Amino Acid Pairs (CKSAAP) feature extraction
# Based on many aspects of assessments, we found the CKSAAP was more suitable for encoding the protein sequence
!python iFeature/iFeature.py --file benchmarking.txt --type CKSAAP --out CKSAAP.txt

input_file2 = "CKSAAP.txt"

file1 = open(input_file2, 'r')

Lines = file1.readlines()

id = [np.array(line.split()[0]) for line in Lines]

data = {'ID': id}
df_KSAAP = pd.DataFrame(data)     

for i in tqdm(range(len(Lines[0].split())-1)):
  feat_vect = [np.array(line.split()[i+1]) for line in Lines]
  feat_name = Lines[0].split()[i+1]
  df_KSAAP[feat_name] = feat_vect


df_KSAAP['ID'] = id    
df_KSAAP= df_KSAAP.iloc[1: , :]
df_KSAAP.head()

"""## AAINDEX

We were not able to include AAINDEX unfortunately, even with the methods we mentioned in class (using a GPU node on the DCC, parallelizing the task). Loading in the data into a dataframe was one issue, and training was an entirely even bigger issue that we could not get working in this timeframe.
"""

#Amino Acid Index feature extraction
!python iFeature/iFeature.py --file alt_benchmarking.txt --type AAINDEX --out AAINDEX.txt

input_file2 = "AAINDEX.txt"

file1 = open(input_file2, 'r')

Lines = file1.readlines()

id = [np.array(line.split()[0]) for line in Lines]

data = {'ID': id}
df_AAI = pd.DataFrame(data)     

#len(Lines[0].split())-1)/10)

from joblib import Parallel

with Parallel(n_jobs = 16) as parallel:
  for i in tqdm(range(len(Lines[0].split())-1)):
    feat_vect = [np.array(line.split()[i+1]) for line in Lines]
    feat_name = Lines[0].split()[i+1]
    df_AAI[feat_name] = feat_vect


df_AAI['ID'] = id    
df_AAI= df_AAI.iloc[1: , :]
df_AAI.head()

with Pool(5) as p:
  p.map()

"""# MLP

## Creating training and test data
"""

# test size set to 0.3
df_final = pd.concat([df_AAC, df_CTDT, df_DPC,df_KSAAP], axis=1)
df_final = df_final.drop(columns = ['ID'])
train, test, train_label, test_label = train_test_split(df_final,label,  test_size=0.3,random_state=0)

"""## Grid search for hyper param"""

from sklearn.model_selection import ParameterGrid

"""Due to large run times, features were found on a standard model instead of through cross valididation grid search. Also due to large run times, the features were searched one at a time. The grid search priotitized ROC AUC score since this was the metric that the original paper focused on the most. First, the best hidden layers size was found. Below is just a sample of the hidden layers our group tried."""

parameters={
'hidden_layer_sizes': [(200,200,200,200),(300,250,200,150,100),(200,200,200,200,200,200,200,200),(300,300,300,300,300),(200,200,200,200,200),(200,200,200,200,200,200)]
}

def evaluate_model(model, params):
  score = np. array([])
  candidate_params = list(ParameterGrid(params))
  for i, p in enumerate(candidate_params):
    mlp =  model(**p, random_state=0)
    mlp = mlp.fit(train,train_label)
    y_pred = mlp.predict_proba(test)
    accuracy = metrics.roc_auc_score(test_label, y_pred[:,1])
    score = np.append(score, np.array(accuracy))
  return candidate_params[np.argmax(score)]

best_para = evaluate_model(MLPClassifier, parameters)
print('Best parameter combination is ', best_para)

"""Once the best hidden layer arangement was found, the below parameters were placed into the grid search. The best parameters were found from the grid search and placed into the variable, best para."""

parameters={
'hidden_layer_sizes': [(200,200,200,200)],
'activation': ['relu','logistic','tanh'],
'solver':['adam','sgd'],
'learning_rate': ['constant','adaptive'],
'learning_rate_init':[.0015,.001,.0008,.002],
'max_iter': [20,50,100,200,300,400],
'batch_size': [50,200,400]}

#best_para = evaluate_model(MLPClassifier, parameters)

best_para={
'hidden_layer_sizes': [(200,200,200)],
'learning_rate_init':[.001],
'max_iter': [20],
'batch_size': [200],
'learning_rate': ['constant'],
'activation': ['logistic']}

print('Best parameter combination is ', best_para)

best_model = MLPClassifier(**best_para,random_state=0)
best_model = best_model.fit(train,train_label)
best_y_pred_proba = best_model.predict_proba(test)
best_y_pred = best_model.predict(test)

print("ROC score:",metrics.roc_auc_score(test_label, best_y_pred_proba[:,1]))
acc_MLP, precision_MLP, sensitivity_MLP, specificity_MLP, MCC_MLP  = calculate_performance(len(test), test_label, best_y_pred)
print('Accuracy is {}\n'.format(acc_MLP),"Precision is {}\n".format(precision_MLP), 'Sensitivity is {}\n'.format(sensitivity_MLP), 'Specificity is {}\n'. format(specificity_MLP), 'MCC is {}\n'.format(MCC_MLP))

"""These are the scores for the model without cross validation. The scores are based on the scores used in the original paper. These scores will be analyzed more after cross validation.

## 5 fold cross validation
"""

best_para = {'activation': 'relu', 'batch_size': 200, 'hidden_layer_sizes': (200, 200, 200, 200, 200), 'learning_rate': 'constant', 'learning_rate_init': 0.001, 'max_iter': 20, 'solver': 'adam'}

from numpy import mean
from numpy import std
from sklearn.datasets import make_classification
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ParameterGrid
# prepare the cross-validation procedure. 5 Splits
cv = KFold(n_splits=5, random_state=1, shuffle=True)
# create model
model = MLPClassifier(**best_para, random_state=0)

scoring = ['recall','accuracy','roc_auc', 'balanced_accuracy']
#finds the recall, accuracy, roc auc, and balanced accuracy for 5 fold CV
scores = sklearn.model_selection.cross_validate(model, df_final, label, scoring=scoring, cv=cv, n_jobs=1)
#finds the specificity and MCC for 5 fold CV
scoring2 = {
    'specificity': metrics.make_scorer(metrics.recall_score,pos_label=0),
    'mcc': metrics.make_scorer(metrics.matthews_corrcoef)}
scores2 = sklearn.model_selection.cross_validate(model, df_final, label, scoring=scoring2, cv=cv, n_jobs=1)

#print scoring for MLP
scoring2_names = ['specificity','mcc']
for i in range(len(scoring)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring[i],np.mean(scores[list(scores)[i+2]]),np.std(scores[list(scores)[i+2]])))
for i in range(len(scoring2)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring2_names[i], np.mean(scores2[list(scores2)[i+2]]),np.std(scores2[list(scores2)[i+2]])))

"""The MLP has scored high on specificity. The accuracy is good. The ROC AUC is good, but below most ROC values presented in the original paper. Overall, our group was dissapointed in the performance of the MLP model. The poor preformance may be attributed to the lack of training data. In the future, feature reduction can be preformed to only train the model on the most important features, this could possibly improve performance.

## box and whisker

A visualization for the scores above
"""

import pylab as pl
import scipy.stats
from numpy import mean
from numpy import std
from sklearn.datasets import make_classification
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ParameterGrid

plt.boxplot([scores['test_recall'],scores['test_accuracy'],scores['test_roc_auc'],scores2['test_specificity'],scores2['test_mcc'], scores['test_balanced_accuracy']])
plt.xticks([1,2,3,4,5,6], ['recall', 'accuracy','roc_auc','specificity','mcc', 'balanced'])
plt.title('Distribution of metrics for 5-fold validated model')
plt.show()

"""## ROC Curve"""

from sklearn.metrics import roc_curve, auc
plot_roc_curve(test_label, best_y_pred_proba[:,1], 'proposed method')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([-0.05, 1])
plt.ylim([0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC')
plt.legend(loc="lower right")
# plt.savefig(save_fig_dir + selected + '_' + class_type + '.png')
plt.show()

"""ROC Curve for the standard MLP model. ROC is above .5 so the model is preforming better than random; however, this score is lower compared to the models from the original paper. It is only similar in value to the worst preforming models from the original paper. The curve does not have a high slope in the begining of the graph so it is possible that this model would also have a low BEDROC score.

# Ensemble Model

## Finding the rf and SVM hyperparameters
"""

# parameters to be used in the grid search
parameters_rf={
'min_samples_leaf': [3, 4, 5],
'min_samples_split': [8, 10, 12],
'n_estimators': [100, 200, 300, 1000]
}

# parameters to be used in the grid search
parameters_svm = {'C': [0.1,1, 10], 'gamma': [1,0.1,0.01],'kernel': ['rbf', 'poly', 'sigmoid']}

def evaluate_model2(model, params):
  score = np. array([])
  candidate_params = list(ParameterGrid(params))
  for i, p in enumerate(candidate_params):
    mlp =  model(**p, random_state=0)
    mlp = mlp.fit(train,train_label)
    y_pred = mlp.predict(test)
    #ROC prioritized since this is what the original paper was focused on
    accuracy = metrics.roc_auc_score(test_label, y_pred)
    score = np.append(score, np.array(accuracy))
  return candidate_params[np.argmax(score)]

#conducting grid search
best_para_rf= evaluate_model2(RandomForestClassifier, parameters_rf)
best_para_SVM = evaluate_model2(svm.SVC, parameters_svm)

print('Best parameter combination is ', best_para_rf)
print('Best parameter combination is ', best_para_SVM)

"""## Training SVM, RF, and GNB"""

#train SVM and get predictions
clf_SVM = svm.SVC(**best_para_SVM, random_state = 0, probability= True)
clf_SVM.fit(train, train_label)
y_pred_SVM = clf_SVM.predict(test)
predicted_probs_svm = clf_SVM.predict_proba(test) 

#train gnb and get predictions
gnb = GaussianNB()
gnb.fit(train, train_label)
y_pred_gnb = gnb.predict(test)
predicted_probs_gnb = gnb.predict_proba(test)

#train RF and get predictions
rf = RandomForestClassifier(**best_para_rf, random_state = 0)
rf.fit(train,train_label)
y_pred = rf.predict(test)
predicted_probs_rf = rf.predict_proba(test)

"""## Ensemble Creation and testing"""

# weights for the ensemble model [SVM,GNB,RF]
# RF is weighted highest since it has the by far best performance of the 3. SVM performed the second best.
weights = [50, 5, 500]

# models to be used for ensemble model
clf_SVM = svm.SVC(**best_para_SVM, random_state = 0, probability= True)
gnb = GaussianNB()
rf = RandomForestClassifier(**best_para_rf, random_state = 0)

# training the ensemble model
ens = sklearn.ensemble.VotingClassifier(estimators = [('svm',clf_SVM),('gnb',gnb),('rf',rf)],voting='soft',weights=weights)
ens = ens.fit(train, train_label)
ens_predict = ens.predict(test)
ens_predict_proba= ens.predict_proba(test)

print("ENS ROC score:",metrics.roc_auc_score(test_label, ens_predict_proba[:,1]))
acc_ens, precision_ens, sensitivity_ens, specificity_ens, MCC_ens  = calculate_performance(len(test), test_label, ens_predict)
print('Accuracy is {}\n'.format(acc_ens),"Precision is {}\n".format(precision_ens), 'Sensitivity is {}\n'.format(sensitivity_ens), 'Specificity is {}\n'. format(specificity_ens), 'MCC is {}\n'.format(MCC_ens))

"""Scores for the basic Ensemble model. The scores are the same as the original paper and same one for the MLP. These scores look promising as the ROC is close to the original authors and much better than the MLP.

## testing each component

Looking at the scores for the three components of the ensemble model. These are just the basic scores and more analysis conducted for the 5 fold cross validation.
"""

print("SVM ROC score:",metrics.roc_auc_score(test_label, predicted_probs_svm[:,1]))
acc_SVM, precision_SVM, sensitivity_SVM, specificity_SVM, MCC_SVM  = calculate_performance(len(test), test_label, y_pred_SVM)
print('Accuracy is {}\n'.format(acc_SVM),"Precision is {}\n".format(precision_SVM), 'Sensitivity is {}\n'.format(sensitivity_SVM), 'Specificity is {}\n'. format(specificity_SVM), 'MCC is {}\n'.format(MCC_SVM))

print("GNB ROC score:",metrics.roc_auc_score(test_label, predicted_probs_gnb[:,1]))
acc_gnb, precision_gnb, sensitivity_gnb, specificity_gnb, MCC_gnb  = calculate_performance(len(test), test_label, y_pred_gnb)
print('Accuracy is {}\n'.format(acc_gnb),"Precision is {}\n".format(precision_gnb), 'Sensitivity is {}\n'.format(sensitivity_gnb), 'Specificity is {}\n'. format(specificity_gnb), 'MCC is {}\n'.format(MCC_gnb))

print("RF ROC score:",metrics.roc_auc_score(test_label, predicted_probs_rf[:,1]))
acc_rf, precision_rf, sensitivity_rf, specificity_rf, MCC_rf  = calculate_performance(len(test), test_label, y_pred)
print('Accuracy is {}\n'.format(acc_rf),"Precision is {}\n".format(precision_rf), 'Sensitivity is {}\n'.format(sensitivity_rf), 'Specificity is {}\n'. format(specificity_rf), 'MCC is {}\n'.format(MCC_rf))

"""## 5 fold"""

from numpy import mean
from numpy import std
from sklearn.datasets import make_classification
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ParameterGrid

# prepare the cross-validation procedure 5 fold split
cv = KFold(n_splits=5, random_state=1, shuffle=True)

#Specificying scoring metrics

ens = sklearn.ensemble.VotingClassifier(estimators = [('svm',clf_SVM),('gnb',gnb),('rf',rf)],voting='soft', weights = weights)
scoring = ['recall','accuracy','roc_auc', 'balanced_accuracy']
scores_ens = sklearn.model_selection.cross_validate(ens, df_final, label, scoring=scoring, cv=cv, n_jobs=1)
scoring2 = {
    'specificity': metrics.make_scorer(metrics.recall_score,pos_label=0),
    'mcc': metrics.make_scorer(metrics.matthews_corrcoef)}
scores2_ens = sklearn.model_selection.cross_validate(ens, df_final, label, scoring=scoring2, cv=cv, n_jobs=1)

#Printing out scoring metrics

scoring2_names = ['specificity','mcc']
for i in range(len(scoring)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring[i],np.mean(scores_ens[list(scores_ens)[i+2]]),np.std(scores_ens[list(scores_ens)[i+2]])))
for i in range(len(scoring2)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring2_names[i], np.mean(scores2_ens[list(scores2_ens)[i+2]]),np.std(scores2_ens[list(scores2_ens)[i+2]])))

"""Score for the Ensemble model. The ROC AUC and specificity is high. The accuracy is high. The recall is lower than the MLP; however, the ensemble was a much more succesful model.

### RF
"""

#Specifying scoring
scores_rf = sklearn.model_selection.cross_validate(rf, df_final, label, scoring=scoring, cv=cv, n_jobs=1)
scores2_rf = sklearn.model_selection.cross_validate(rf, df_final, label, scoring=scoring2, cv=cv, n_jobs=1)

#Printing out scoring metrics
for i in range(len(scoring)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring[i],np.mean(scores_rf[list(scores_rf)[i+2]]),np.std(scores_rf[list(scores_rf)[i+2]])))
for i in range(len(scoring2)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring2_names[i], np.mean(scores2_rf[list(scores2_rf)[i+2]]),np.std(scores2_rf[list(scores2_rf)[i+2]])))

"""This portion of the ensemble model is performing the best and is weighted highly for that reason. AUC, accuracy, recall, and specificity is similarily high to the ensemble.

### gnb
"""

#Specifying scoring

scores_gnb = sklearn.model_selection.cross_validate(gnb, df_final, label, scoring=scoring, cv=cv, n_jobs=1)
scores2_gnb = sklearn.model_selection.cross_validate(gnb, df_final, label, scoring=scoring2, cv=cv, n_jobs=1)

#Printing out scoring metrics
for i in range(len(scoring)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring[i],np.mean(scores_gnb[list(scores_gnb)[i+2]]),np.std(scores_gnb[list(scores_gnb)[i+2]])))
for i in range(len(scoring2)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring2_names[i], np.mean(scores2_gnb[list(scores2_gnb)[i+2]]),np.std(scores2_gnb[list(scores2_gnb)[i+2]])))

"""The worst perfoming portion of the ensemble model, and is weighted the lowest for that reason. ROC was lower than the MLP. ROC, accuracy, and MCC are all the worst performing portion of the ensemble model. Recall is higher than the other portions.

### svm
"""

#Specifying scoring
scores_svm = sklearn.model_selection.cross_validate(clf_SVM, df_final, label, scoring=scoring, cv=cv, n_jobs=1)
scores2_svm = sklearn.model_selection.cross_validate(clf_SVM, df_final, label, scoring=scoring2, cv=cv, n_jobs=1)

#Printing out scoring metrics
for i in range(len(scoring)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring[i],np.mean(scores_svm[list(scores_svm)[i+2]]),np.std(scores_svm[list(scores_svm)[i+2]])))
for i in range(len(scoring2)):
  print('{} mean is {:.3f} with std of {:.3f}'.format(scoring2_names[i], np.mean(scores2_svm[list(scores2_svm)[i+2]]),np.std(scores2_svm[list(scores2_svm)[i+2]])))

"""This portion of the ensemble model is not perfoming best, but is not performing the worst. It is performing better than the MLP.

## box plot

Visualizations for the scores for the Ensemble, RF, GNB, and SVM models.
"""

plt.boxplot([scores_ens['test_recall'],scores_ens['test_accuracy'],scores_ens['test_roc_auc'],scores2_ens['test_specificity'],scores2_ens['test_mcc'], scores_ens['test_balanced_accuracy']])
plt.xticks([1,2,3,4,5,6], ['recall', 'accuracy','roc_auc','specificity','mcc', 'balanced'])
plt.title('Distribution of metrics for 5-fold Ensemble model')
plt.show()

plt.boxplot([scores_rf['test_recall'],scores_rf['test_accuracy'],scores_rf['test_roc_auc'],scores2_rf['test_specificity'],scores2_rf['test_mcc'], scores_rf['test_balanced_accuracy']])
plt.xticks([1,2,3,4,5,6], ['recall', 'accuracy','roc_auc','specificity','mcc', 'balanced'])
plt.title('Distribution of metrics for 5-fold RF model')
plt.show()

plt.boxplot([scores_svm['test_recall'],scores_svm['test_accuracy'],scores_svm['test_roc_auc'],scores2_svm['test_specificity'],scores2_svm['test_mcc'], scores_svm['test_balanced_accuracy']])
plt.xticks([1,2,3,4,5,6], ['recall', 'accuracy','roc_auc','specificity','mcc', 'balanced'])
plt.title('Distribution of metrics for 5-fold SVM model')
plt.show()

plt.boxplot([scores_gnb['test_recall'],scores_gnb['test_accuracy'],scores_gnb['test_roc_auc'],scores2_gnb['test_specificity'],scores2_gnb['test_mcc'], scores_gnb['test_balanced_accuracy']])
plt.xticks([1,2,3,4,5,6], ['recall', 'accuracy','roc_auc','specificity','mcc', 'balanced'])
plt.title('Distribution of metrics for 5-fold GNB model')
plt.show()

"""## ROC Curve"""

plot_roc_curve(test_label,ens_predict_proba[:,1], 'proposed method')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([-0.05, 1])
plt.ylim([0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC')
plt.legend(loc="lower right")
plt.show()

"""ROC curve for the basic Ensemble model. The model is perfoming better than random. The curve has a high slope in the begining, which means that the BEDROC could possibly be higher for the Ensemble than the MLP that did not have such a high slope.

## T Test
"""

import scipy.stats
ttest_ens = scipy.stats.ttest_ind(scores['test_roc_auc'],scores_ens['test_roc_auc'])
ttest_svm = scipy.stats.ttest_ind(scores['test_roc_auc'],scores_svm['test_roc_auc'])
ttest_gnb = scipy.stats.ttest_ind(scores['test_accuracy'],scores_gnb['test_roc_auc'])
ttest_rf = scipy.stats.ttest_ind(scores['test_roc_auc'],scores_rf['test_roc_auc'])
print('P value for MLP compared to Ensemble',ttest_ens[1])
print('P value for MLP compared to SVM',ttest_svm[1])
print('P value for MLP compared to GNB',ttest_gnb[1])
print('P value for MLP compared to RF',ttest_rf[1])

"""T test on the ROC AUC shows that the Ensemble, SVM, and RF outpreforms the MLP created. Once again, ROC was used since this is the metric the original paper focused on. Comparison to  the original paper could not be done because standard deviation was not reported."""

ttest_svm_ens = scipy.stats.ttest_ind(scores_ens['test_roc_auc'],scores_svm['test_roc_auc'])
ttest_gnb_ens = scipy.stats.ttest_ind(scores_ens['test_roc_auc'],scores_gnb['test_roc_auc'])
ttest_rf_ens = scipy.stats.ttest_ind(scores_ens['test_roc_auc'],scores_rf['test_roc_auc'])
print('P value for SVM compared to Ensemble',ttest_svm_ens[1])
print('P value for GNB compared to Ensemble',ttest_gnb_ens[1])
print('P value for RF compared to Ensemble',ttest_rf_ens[1])

"""T test done on the AUC for the Ensemble compared to the other components of the model. This shows that the ensemble is outperforming the SVM and GNB portion of the model. The ensemble had a higher mean for AUC scores after 5 fold cross validation. However, RF is not stastically different than the Ensemble model. This is probably due to the high weighting of the RF for the Ensemble. This was done since the RF outperforms the other two portions so highly. An unfoutanate consequence of this is that RF dominates the ensemble response.

For this project we set out to prove that a more complex model such as an MLP or an ensemble model can outperfom the random forest model presented in the paper. Overall we found that the more complex models were either outperformed by RF, in the case of the MLP, or performed the same as RF, in the case of the ensemble.

## Outdated Code
"""

parameters={
'hidden_layer_sizes': [(200,200,200,200)],
'learning_rate_init':[.0015],
'max_iter': [20],
'batch_size': [200],
'learning_rate': ['constant'],
'solver':['adam'],
'activation': ['relu']}


#candidate_params = list(ParameterGrid(params))

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
oHe = OneHotEncoder()
ct = ColumnTransformer(transformers=[('encode',oHe,[0])],remainder='passthrough')
dataset = np.array(ct.fit_transform(train))

from sklearn.model_selection import GridSearchCV

X_train, X_test, y_train, y_test = train_test_split(df_final, label, random_state=0)

#import matplotlib.pyplot as plt
#%matplotlib inline

param_grid = ParameterGrid(parameters)
print(param_grid)
grid = GridSearchCV(MLPClassifier(), param_grid, cv=10)
grid.fit(np.array(train), train_label)
print("Best cross-validation score: {:.2f}".format(grid.best_score_))
print("Best parameters: ", grid.best_params_)

import pandas as pd
pvt = pd.pivot_table(pd.DataFrame(grid.cv_results_),
    values='mean_test_score', index='param_alpha', columns='param_l1_ratio')

ax = sns.heatmap(pvt)

yhats = [model.predict(test) for model in members]

weights = [.1, .2, .7]
np.array(yhats).shape
summed = tensordot(yhats, weights, axes=((0),(0)))
summed.shape

from itertools import product
from numpy.linalg import norm
from numpy import tensordot
from numpy import argmax
from sklearn.metrics import accuracy_score


def ensemble_predictions(members, weights, testX):
  result =  []
  # make predictions
  yhats = [model.predict(testX) for model in members]
  yhats = np.array(yhats)
  # weighted sum across ensemble members
  summed = tensordot(yhats, weights, axes=((0),(0)))
  print('Summed is good')
  for i in range(len(summed)):
    if summed[i] >.5:
      result.append(1)
    else:
      result.append(0) 
  return result


def evaluate_ensemble(members, weights, testX, testy):
  # make prediction
  yhat = ensemble_predictions(members, weights, testX)
  print('Evaluate good')
  # calculate accuracy
  return accuracy_score(testy, yhat)


def normalize(weights):
	# calculate l1 vector norm
	result = norm(weights, 1)
	# check for a vector of all zeros
	if result == 0.0:
		return weights
	# return normalized vector (unit norm)
	return weights / result


def grid_search(members, testX, testy):
  # define weights to consider
  w = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  best_score, best_weights = 0.0, None
  # iterate all possible combinations (cartesian product)
  for weights in product(w, repeat=len(members)):
    # skip if all weights are equal
    if len(set(weights)) == 1:
      continue
    # hack, normalize weight vector
    print('Starting new weights')
    weights = normalize(weights)
    # evaluate weights
    score = evaluate_ensemble(members, weights, testX, testy)
    print('Score is: ')
    print(score)
    if score > best_score:
      
      best_score, best_weights = score, weights
      print('>%s %.3f' % (best_weights, best_score))
  return list(best_weights)

members = [clf_SVM, gnb, rf]
weights = grid_search(members, test, test_label)

y_train.dtype

