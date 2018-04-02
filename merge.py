# -*- coding: utf-8 -*-
#实现了DEM、土地利用数据的拼接、裁剪以及重投影
#输入：tile of DEM and LUCC
#输出：空间分辨率为1000m，坐标信息为WGS84-50N的DEM和LUCC栅格数据


import subprocess
import osr,ogr,gdal,pprint
import numpy as np
from os.path import join
import glob

printer = pprint.PrettyPrinter(indent=3)

data_dir = "/home/lan/data_pool/orange/LUCC"
original_file = "/home/lan/data_pool/orange/LUCC/original_LUCC2010.tif"
mid_file = "/home/lan/data_pool/orange/LUCC/mid_LUCC2010.tif"
result_file = "/home/lan/data_pool/orange/LUCC/result_LUCC2010.tif"

target_file = glob.glob(join(data_dir,"*","*_1km_Majority.tif"))
target_file.sort()
printer.pprint(target_file)

subprocess.call(['gdal_merge.py','-o',original_file,*target_file])

RasterFormat = 'GTiff'
PixelRes = 1000
minX = -178683.569224
maxX = 839316.430776
minY = 3273803.5777
maxY = 4117803.5777

subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84',\
'-r','bilinear',original_file,mid_file])

Raster = gdal.Open(mid_file)
Projection = Raster.GetProjectionRef()

OutTile = gdal.Warp(result_file, Raster, format=RasterFormat, outputBounds=[minX, minY, maxX, maxY],\
xRes=1000, yRes=1000, dstSRS=Projection, resampleAlg=gdal.GRA_Bilinear)
OutTile = None
Raster = None
