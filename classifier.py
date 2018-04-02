# -*- coding: utf-8 -*-
# 模型建立时输入数据为样本点的文件，模型预测时输入文件为13个栅格数据集
# 输出结果为模型的预测结果，为栅格数据

import os
import sys
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *
from os.path import join
import pdb
import pandas as pd
import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm

immutable_dir = "/home/lan/data_pool/orange/immutable"
variable_dir = "/home/lan/data_pool/orange/variable"
vegetation_wetness = "/home/lan/data_pool/orange/vegetation_wetness"
train = pd.read_csv("/home/lan/data_pool/orange/sample.csv")

def get_headers(dataset):
     return dataset.columns.values

def add_headers(dataset, headers):
     dataset.columns = headers
     return dataset

headers = ["ID","DEM", "LUCC","aspect","pop", "rail","riv","road","sett","slope","Tmax","Tmin","pre","wetness","conf"]
train_adderheader = add_headers(train, headers)

cols = ["DEM", "LUCC","aspect","pop", "rail","riv","road","sett","slope","Tmax","Tmin","pre","wetness"]
colsRes = ["conf"]
trainArr = train_adderheader.as_matrix(cols) #training array
trainRes = train_adderheader.as_matrix(colsRes) # training results

#  Training
clf = svm.SVC(C=1.0,
              kernel='rbf',
              degree=3,
              gamma='auto',
              coef0=0.0,
              shrinking=True,
              probability=False,
              tol=0.001,
              cache_size=1024,
              class_weight='balanced',
              verbose=False,
              max_iter=-1,
              decision_function_shape='ovr',
              random_state=None)
clf.fit(trainArr, trainRes.ravel())
# RF = RandomForestClassifier(n_estimators = 1000,max_features = 3) # initialize
# RF.fit(trainArr, trainRes.ravel()) # fit the data to the algorithm
print ("training is  over")
# print(RF.feature_importances_)

# Extract band's data and transform into a numpy array
immutable_file = glob.glob(join(immutable_dir,"*","*.tif"))
immutable_file.sort()
col = 1018
row = 844
bandsData = []
for factor in immutable_file:
    print(factor)
    factor_file = gdal.Open(factor)
    arrband = factor_file.GetRasterBand(1)
    bandsData.append(arrband.ReadAsArray(0,0,col,row))

Tmax_file = glob.glob(join(variable_dir,"Tmax","*.tif"))
Tmin_file = glob.glob(join(variable_dir,"Tmin","*.tif"))
pre_file = glob.glob(join(variable_dir,"preci","*.tif"))
Tmax_file.sort()
Tmin_file.sort()
pre_file.sort()
length = len(Tmax_file)
# for i in range(length):
#test day = 2016225
if (Tmax_file[164].split("/")[-1]==Tmin_file[164].split("/")[-1]) and (Tmax_file[164].split("/")[-1] == pre_file[164].split("/")[-1]):
    tamx_file = gdal.Open(Tmax_file[164])
    tmaxband = tamx_file.GetRasterBand(1)
    bandsData.append(tmaxband.ReadAsArray())

    tmin_file = gdal.Open(Tmin_file[164])
    tminband = tmin_file.GetRasterBand(1)
    bandsData.append(tminband.ReadAsArray())

    pre_file = gdal.Open(pre_file[164])
    preband = pre_file.GetRasterBand(1)
    bandsData.append(preband.ReadAsArray())

for wetness_file in os.listdir(vegetation_wetness):
    target = Tmax_file[164].split("/")[-1].split(".")[0]
    if ((int(wetness_file.split(".")[0])+ 8) > int(target))and (int(wetness_file.split(".")[0]) <= int(target)):
        w_ = join(vegetation_wetness,wetness_file)
        wet_file = gdal.Open(w_)
        wetband = wet_file.GetRasterBand(1)
        bandsData.append(wetband.ReadAsArray())
    else:
        continue
bandsData = np.dstack(bandsData)
row, col, noBands = bandsData.shape
print(row,col,noBands)
noSamples = row*col
flat_pixels = bandsData.reshape((noSamples, noBands))
print("start to predict!")

# result = RF.predict(flat_pixels)
result = clf.predict(flat_pixels)
print(result.shape)
classification = result.reshape((row, col))

testfile = gdal.Open(Tmax_file[0], GA_ReadOnly)  # open a dir
geomatrix = testfile.GetGeoTransform()
projection = testfile.GetProjectionRef()

#creat a raster image to store the classification result
driver = gdal.GetDriverByName('GTiff')
gdal.AllRegister()
outRaster = join("/home/lan/data_pool/orange","2016164-3.tif")
rasterDS = driver.Create(outRaster, col, row, 1, GDT_Int16)
rasterDS.SetGeoTransform(geomatrix)
rasterDS.SetProjection(projection)
rasterDS.GetRasterBand(1).WriteArray(classification)
