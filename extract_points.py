# -*- coding: utf-8 -*-
#输入为每个点的坐标信息
#输出为每个点对应的13feature的value

import math
import os
import sys
import numpy
from osgeo import gdal
from osgeo.gdalconst import *
import csv
import struct
import pdb
from os.path import join
import pandas as pd
import better_exceptions
import glob

# extract points one by one band
def pt2fmt(pt):
    fmttypes = {GDT_Byte: 'B',GDT_Int16: 'h',GDT_UInt16: 'H',GDT_Int32: 'i',GDT_UInt32: 'I',GDT_Float32: 'f',GDT_Float64: 'f'}
    return fmttypes.get(pt, 'x')
fire_dir = "/home/lan/data_pool/orange/sample_point.csv"
immutable_dir = "/home/lan/data_pool/orange/immutable"
variable_dir = "/home/lan/data_pool/orange/variable"
wetness_dir = "/home/lan/data_pool/orange/vegetation_wetness"

col = 1018
row = 844
immutable_file = glob.glob(join(immutable_dir,"*","*.tif"))
immutable_file.sort()
# print(immutable_file)
dictpoints = {}
for filee in immutable_file:
    print(filee)
    bands = gdal.Open(filee)
    bandsdata = bands.GetRasterBand(1)
    with open(fire_dir) as f:
        next(f)
        for line in f:
            seg = line.strip().split(',')
            px = int(seg[1])
            py = int(seg[2])
            dt = seg[4]
            key1 = str(px) + "-" + str(py) +"-" + dt
            if px > col or py > row:
                continue
            result = bandsdata.ReadRaster(px-1, py-1, 1, 1,buf_type=bandsdata.DataType)
            fmt = pt2fmt(bandsdata.DataType)
            intval = struct.unpack(fmt, result)
            value = intval[0]
            dictpoints.setdefault(key1, []).append(value)

for v_folder in os.listdir(variable_dir):
    print(v_folder)
    v_ = join(variable_dir,v_folder)
    for filee in os.listdir(v_):
        bands = gdal.Open(join(v_,filee))
        bandsdata = bands.GetRasterBand(1)
        with open(fire_dir) as f:
            next(f)
            for line in f:
                seg = line.strip().split(',')
                if filee.split(".")[0] != seg[4]:
                    continue
                else:
                    px = int(seg[1])
                    py = int(seg[2])
                    dt = seg[4]
                    key1 = str(px) + "-" + str(py) +"-" + dt
                    if px > col or py > row:
                        continue
                    result = bandsdata.ReadRaster(px-1, py-1, 1, 1,buf_type=bandsdata.DataType)
                    fmt = pt2fmt(bandsdata.DataType)
                    intval = struct.unpack(fmt, result)
                    value = intval[0]
                    dictpoints.setdefault(key1, []).append(value)
for wetness_file in os.listdir(wetness_dir):
    print(" process vegetation_wetness")
    w_ = join(wetness_dir,wetness_file)
    bands = gdal.Open(w_)
    bandsdata = bands.GetRasterBand(1)
    with open(fire_dir) as f:
        next(f)
        for line in f:
            seg = line.strip().split(',')
            if ((int(wetness_file.split(".")[0])+ 8) > int(seg[4]))and ((int(wetness_file.split(".")[0])) <= int(seg[4])):
                px = int(seg[1])
                py = int(seg[2])
                dt = seg[4]
                key1 = str(px) + "-" + str(py) +"-" + dt
                if px > col or py > row:
                    continue
                result = bandsdata.ReadRaster(px-1, py-1, 1, 1,buf_type=bandsdata.DataType)
                fmt = pt2fmt(bandsdata.DataType)
                intval = struct.unpack(fmt, result)
                value = intval[0]
                dictpoints.setdefault(key1, []).append(value)
                if len(dictpoints[key1]) > 12:
                    dictpoints.setdefault(key1, []).append(int(seg[3]))

dataset = pd.DataFrame.from_dict(data = dictpoints,orient = 'index')
dataset .to_csv(join("/home/lan/data_pool/orange",'sample.csv'),header = False)
print ("process is over")
