# -*- coding: utf-8 -*-

#输入数据为railway、river、roads、settlement的矢量数据
#输出数据为每个像元到最近的railway、river、roads、settlement的距离的栅格数据

from osgeo import ogr,gdal,osr
import os
import sys
import subprocess
from osgeo.gdalconst import *

minX = -178683.569224
maxX = 839316.430776
minY = 3273803.5777
maxY = 4117803.5777


Shapefile_in = "/home/lan/data_pool/river"
Rasterfile_out = "/home/lan/data_pool/river/river.tif"
project_file = "/home/lan/data_pool/river/river_project.tif"
distance_file = "/home/lan/data_pool/river/river_distance.tif"
result_file = "/home/lan/data_pool/river/river_result.tif"


subprocess.call(['gdal_rasterize','-a','OBJECTID','-tr','0.008333','0.008333',Shapefile_in,Rasterfile_out])

subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84','-tr','1000','1000','-r','bilinear',Rasterfile_out,project_file])
#
subprocess.call(['gdal_proximity.py',project_file,distance_file,'-ot','Float32','-distunits','GEO'])
Raster = gdal.Open(distance_file)
Projection = Raster.GetProjectionRef()
result = gdal.Warp(result_file, Raster, outputBounds=[minX, minY, maxX, maxY],\
xRes=1000, yRes=1000, dstSRS=Projection, resampleAlg=gdal.GRA_Bilinear)
result = None
Raster = None
if os.path.exists(Rasterfile_out):
    os.remove(Rasterfile_out)
if os.path.exists(project_file):
    os.remove(project_file)
if os.path.exists(distance_file):
    os.remove(distance_file)    
