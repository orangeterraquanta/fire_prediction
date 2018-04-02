# -*- coding: utf-8 -*-
# 输入为研究区的经纬度范围
# 输出为研究区选择的非火点坐标以及异常点坐标的合并文件

import os,sys
from osgeo import gdal
import random
import pandas as pd
import csv
from os.path import join

# get no fire points from temperature
data_dir = "/home/lan/data_pool/orange/variable/preci"
fire_csv = "/home/lan/data_pool/orange/fire_point/fire_points.csv"
fire_final = "/home/lan/data_pool/orange/fire_point/fire_final.csv"

example_file = "/home/lan/data_pool/orange/variable/preci/2016061.tif"
example_band = gdal.Open(example_file)
geomatrix = example_band.GetGeoTransform()
cols = example_band.RasterXSize
rows= example_band.RasterYSize

fire_points = []
with open(fire_csv) as f:
    next(f)
    for line in f:
        seg = line.strip().split(',')
        lon = float(seg[1])
        lat = float(seg[2])
        px = int((lon - geomatrix[0])/geomatrix[1])+1
        py = int((lat - geomatrix[3])/geomatrix[5])+1
        str1 = (px,py,int(seg[3]),seg[4])
        fire_points.append(str1)
fire_points = list(set(fire_points))

mid = pd.DataFrame(data = fire_points)
mid.to_csv(fire_final)

fire_test = []
with open(fire_final) as f:
    next(f)
    for line in f:
        seg = line.strip().split(',')
        str2 = str([1]) + str(seg[2]) + seg[4]
        fire_test.append(str2)

with open(fire_final) as ff:
    reader = csv.DictReader(ff)
    column = [row['3'] for row in reader]
fire_number = len(column)
fire_date = set(column)
date_number = len(list(fire_date))
sample_size = int(fire_number * 3 /date_number)

result = []
for nofire_file in os.listdir(data_dir):
    if nofire_file.split(".")[0] in fire_date:
        dt = nofire_file.split(".")[0]
        points = [(row,col)for row in range(rows) for col in range(cols)]
        random.shuffle(points)
        for row,col in points[:sample_size]:
            str3 = str(col) + str(row) + dt
            if str3 in fire_test:
                print("same to fire point")
                continue
            result.append((col,row,0,dt))
result = list(set(result))
mid = pd.DataFrame(data = result)
no_fire = join("/home/lan/data_pool/orange","nofire.csv")
mid.to_csv(no_fire)
# merge two csv files
readers = csv.DictReader(open(no_fire))
headers = readers.fieldnames
with open(fire_final,'a') as fcsv :
    writer = csv.DictWriter(fcsv,fieldnames = headers)
    writer.writerows(readers)
