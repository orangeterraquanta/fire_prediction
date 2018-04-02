# -*- coding: utf-8 -*-
# 目的是利用ROC曲线评价模型的模拟性能
# 输入为实测值与预测值
# 输出为 ROC曲线
import csv
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve,auc
from sklearn import svm
import matplotlib.pyplot as plt

example = "/home/lan/data_pool/orange/TEST.csv"
train_test = []
with open(example) as f:
    next(f)
    for line in f:
        seg = line.strip().split(',')
        # print(seg[14])
        if int(seg[14]) > 40:
            seg[14] = '1'
        else:
            seg[14] = '0'
        str2 = seg
        train_test.append(str2)
mid = pd.DataFrame(data = train_test)
no_fire = "/home/lan/data_pool/orange/TEST2.csv"
mid.to_csv(no_fire)
train = pd.read_csv(no_fire)

def get_headers(dataset):
     return dataset.columns.values

def add_headers(dataset, headers):
     dataset.columns = headers
     return dataset

headers = ["a","ID","DEM", "LUCC","aspect","pop", "rail","riv","road","sett","slope","Tmax","Tmin","pre","wetness","conf"]
train = add_headers(train, headers)
#
cols = ["DEM", "LUCC","aspect","pop", "rail","riv","road","sett","slope","Tmax","Tmin","pre","wetness"]
colsRes = ["conf"]
#
trainArr = train.as_matrix(cols)
trainRes = train.as_matrix(colsRes).ravel() # training results
X_train,X_test,y_train,y_test = train_test_split(trainArr,trainRes,test_size = 0.5,random_state = 0)
clf = svm.SVC(C=1.0,
              kernel='rbf',
              degree=3,
              gamma='auto',
              coef0=0.0,
              shrinking=True,
              probability=True,
              tol=0.001,
              cache_size=1024,
              class_weight='balanced',
              verbose=False,
              max_iter=-1,
              decision_function_shape='ovr',
              random_state=0)
y_score = clf.fit(X_train,y_train).decision_function(X_test)

fpr,tpr,th = roc_curve(y_test,y_score)
roc_auc = auc(fpr,tpr)

plt.figure()
lw =2
plt.figure(figsize = (10,10))
plt.plot(fpr,tpr,color = "darkorange",lw = lw,label = "ROC curve(area = %0.2f)"% roc_auc)
plt.xlim = ([0.0,1.0])
plt.ylim = ([0.0,1.0])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Receive operating characteristic example")
plt.legend(loc = "lower right")
plt.show()
