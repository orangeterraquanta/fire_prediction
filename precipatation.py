# -*- coding: utf-8 -*-
# 输入为降雨原始数据
# 输出为每天的降雨数据

import os
import sys
from  netCDF4 import Dataset
from osgeo import ogr,gdal,osr,gdal_array
from gdalconst import *
import numpy as np
from os.path import join
from datetime import date
import subprocess
# specify coords ,WGS84 lat/long
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

PATH = "/home/lan/data_pool/orange/precipitation"
mid_dir = "/home/lan/data_pool/orange/precipitation/mid_dir"
result_dir = "/home/lan/data_pool/orange/variable/preci"

RasterFormat = 'GTiff'
PixelRes = 0.0083333333
minX = 110.000138889
maxX = 120.500138889
minY = 29.5995833333
maxY = 36.9995833333

for year in os.listdir(PATH):
    if year == "2016":
        continue
    for month in os.listdir(join(PATH,year)):
        if month in ["01","02","09","10","11","12"]:
            continue
        for filee in os.listdir(join(PATH,year,month)):
            if filee.split(".")[-1] == "nc4":
                filee_dir = join(PATH,year,month,filee)
                dataset = Dataset(filee_dir,"r")
                name_ = filee.split(".")[4]+".tif"
                NewFileName = join(PATH,year,month,name_)
                dataw = dataset.variables["precipitationCal"][:][:]
                #correct the image !!!!
                prec = np.array(dataw)
                prec = prec.T[::-1]

                lat = dataset.variables["lat"][:].tolist()
                lon = dataset.variables["lon"][:].tolist()

                nx = len(lon)
                ny = len(lat)
                xmin, ymin, xmax, ymax = [min(lon), min(lat), max(lon), max(lat)]
                xres = (xmax - xmin) / float(nx)
                yres = (ymax - ymin) / float(ny)
                geotransform = (xmin, xres, 0, ymax, 0, -yres)
                dst_ds = gdal.GetDriverByName('GTiff').Create(NewFileName, nx, ny, 1, gdal.GDT_Float32)
                dst_ds.SetGeoTransform(geotransform)
                dst_ds.SetProjection(new_cs.ExportToWkt()) # export coords to file
                dst_ds.GetRasterBand(1).WriteArray(prec)
                dst_ds.FlushCache()
                dst_ds = None

                Raster = gdal.Open(NewFileName)
                Projection = Raster.GetProjectionRef()

                day= filee.split(".")[4].split("-")[0][6:]
                _mid = date(int(year),int(month),int(day))-date(int(year),1,1)
                _name = _mid.days +1

                if _name < 10:
                    names = '00'+str(_name)
                elif _name <100 :
                    names ='0'+str(_name)
                else:
                    names =str(_name)

                mid_file = join(mid_dir, year+names+ '.tif')
                OutTile = gdal.Warp(mid_file, Raster, format=RasterFormat, outputBounds=[minX, minY, maxX, maxY],\
                xRes=PixelRes, yRes=PixelRes, dstSRS=Projection, resampleAlg=gdal.GRA_Bilinear)
                OutTile = None
                Raster = None

                result_file = join(result_dir,year+names+ '.tif')
                subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84',\
                '-tr','1000','1000','-r','bilinear',mid_file,result_file])
                print("processing is over")
                # subprocess.call(['gdalwarp','-te','110.000138889','29.5995833333','120.500138889','36.9995833333','-te_srs',\
                # '+proj=utm +zone=50 +north +datum=WGS84','-tr','1000','1000','-r','bilinear',NewFileName,final_file])
