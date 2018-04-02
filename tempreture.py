# -*- coding: utf-8 -*-
#输入为温度的原始数据
#输出为研究区日温度数据
import os
import sys
from  netCDF4 import Dataset
from osgeo import ogr,gdal,osr,gdal_array
from gdalconst import *
import numpy as np
from os.path import join
import subprocess

dir_file = "/home/lan/data_pool/orange/Tmin/tmin.2016.nc"
PATH = "/home/lan/data_pool/orange/Tmin/original"
mid_dir = "/home/lan/data_pool/orange/T-mid_dir"
result_dir = "/home/lan/data_pool/orange/variable/Tmin"


RasterFormat = 'GTiff'
PixelRes = 0.0083333333
minX = 110.000138889
maxX = 120.500138889
minY = 29.5995833333
maxY = 36.9995833333


dataset = gdal.Open(dir_file)
data_geomatrix = dataset.GetGeoTransform()
# data_geomatrix = dataset.GetProjectionRef()
col = dataset.RasterXSize
row = dataset.RasterYSize
nbband = dataset.RasterCount

wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""
new_cs = osr.SpatialReference()
new_cs.ImportFromWkt(wgs84_wkt)

#2016:61-244 ,2017:60-243
nb = 61
print(nbband)
for nb in range(61,245):
    arrband = dataset.GetRasterBand(nb)
    arrayband = arrband.ReadAsArray()
    driver = gdal.GetDriverByName('GTiff')
    gdal.AllRegister()
    outRaster = join(PATH, str(nb) + '.tif')
    rasterDS = driver.Create(outRaster, col, row, 1, GDT_Float32)
    rasterDS.SetGeoTransform(data_geomatrix)
    rasterDS.SetProjection(new_cs.ExportToWkt()) # export coords to file
    rasterDS.GetRasterBand(1).WriteArray(arrayband)   # write r-band to the raster
    rasterDS.FlushCache()                     # write to disk
    rasterDS = None

    Raster = gdal.Open(outRaster)
    Projection = Raster.GetProjectionRef()
    if nb < 10:
        _name = '201600'+str(nb) + '.tif'
    elif nb < 100:
        _name = '20160'+str(nb) + '.tif'
    else:
        _name = '2016'+str(nb) + '.tif'

    mid_file = join(mid_dir, _name)
    OutTile = gdal.Warp(mid_file, Raster, format=RasterFormat, outputBounds=[minX, minY, maxX, maxY],\
    xRes=PixelRes, yRes=PixelRes,dstSRS=Projection, resampleAlg=gdal.GRA_Bilinear)
    OutTile = None
    Raster = None

    result_file = join(result_dir,_name)
    subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84',\
    '-tr','1000','1000','-r','bilinear',mid_file,result_file])
    print("procesing is over")
