# -*- coding: utf-8 -*-
# 输入为MOD09A1的原始影像
# 经过计算NMDI，影像拼接、裁剪、重投影，输出为研究区域的NMDI，空间分辨率为1000M，投影信息为WGS84-50N
import os
import sys
from osgeo import gdal
from os.path import join
import numpy as np
import subprocess
import glob
from datetime import date

RasterFormat = 'GTiff'
minX = -178683.569224
maxX = 839316.430776
minY = 3273803.5777
maxY = 4117803.5777

data_path = "/home/lan/data_pool/orange/Untitled Folder"
result_dir = "/home/lan/data_pool/orange/vegetation_wetness"
hdf_file = glob.glob(join(data_path,"*","*.hdf"))
# genernate NMDI
for filee in hdf_file:
    if filee.split("/")[-1].split(".")[2] not in ["h26v05","h27v05","h27v06","h28v05","h28v06"]:
        continue
    hdf_ds = gdal.Open(filee, gdal.GA_ReadOnly)
    band2 = gdal.Open(hdf_ds.GetSubDatasets()[1][0], gdal.GA_ReadOnly)
    band6 = gdal.Open(hdf_ds.GetSubDatasets()[5][0], gdal.GA_ReadOnly)
    band7 = gdal.Open(hdf_ds.GetSubDatasets()[6][0], gdal.GA_ReadOnly)
    arrband2 = band2.GetRasterBand(1).ReadAsArray()
    arrband6 = band6.GetRasterBand(1).ReadAsArray()
    arrband7 = band7.GetRasterBand(1).ReadAsArray()
    dif = np.subtract(arrband6.astype(float),arrband7.astype(float))
    resultarr = np.divide(np.subtract(arrband2.astype(float), dif),
                np.add(arrband2.astype(float), dif) + 0.00000000000001)

    dir_tokens = filee.split("/")
    file_name = dir_tokens[-1].split(".")
    mid_dir = "/"+"/".join(dir_tokens[0:7])
    mid_name = file_name[2]+"-"+file_name[3]+"-"+file_name[4]
    result_path = join(mid_dir,mid_name+"-NMDI.tif")
    out_ds = gdal.GetDriverByName('GTiff').Create(result_path,
                                                  band2.RasterXSize,
                                                  band2.RasterYSize,
                                                  1,
                                                  gdal.GDT_Float32,
                                                  )
    out_ds.SetGeoTransform(band2.GetGeoTransform())
    out_ds.SetProjection(band2.GetProjectionRef())
    out_ds.GetRasterBand(1).WriteArray(resultarr)
    out_ds = None
# mosaic,reproject and clip the NMDI
for NMDI_folder in os.listdir(data_path):
    # if os.path.exists(join(data_path,NMDI_folder,"reproject_NMDI.tif")):
    #     continue
    NMDI_tif = glob.glob(join(data_path,NMDI_folder,"*.tif"))

    mosaic = join(data_path,NMDI_folder,"mosaic_NMDI.tif")
    subprocess.call(['gdal_merge.py','-o',mosaic,*NMDI_tif])

    reproject = join(data_path,NMDI_folder,"reproject_NMDI.tif")
    mosaic_tif = join(data_path,NMDI_folder,"mosaic_NMDI.tif")
    subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84',\
    '-r','bilinear',mosaic_tif,reproject])

    Raster = gdal.Open(reproject)
    Projection = Raster.GetProjectionRef()
    # if not os.path.exists(join(result_dir,NMDI_folder)):
    #     os.mkdir(join(result_dir,NMDI_folder))
    year = NMDI_folder.split(".")[0]
    month = NMDI_folder.split(".")[1]
    day = NMDI_folder.split(".")[2]
    _mid = date(int(year),int(month),int(day))-date(int(year),1,1)
    _name = _mid.days +1
    if _name < 10:
        names = '00'+str(_name)
    elif _name <100 :
        names ='0'+str(_name)
    else:
        names =str(_name)
    result_file = join(result_dir, year+names+ '.tif')
    OutTile = gdal.Warp(result_file, Raster, format=RasterFormat, outputBounds=[minX, minY, maxX, maxY],\
    xRes=1000, yRes=1000, dstSRS=Projection, resampleAlg=gdal.GRA_Bilinear)
    OutTile = None
    Raster = None
