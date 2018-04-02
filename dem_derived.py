# -*- coding: utf-8 -*-
# 输入为裁剪并投影后的研究区域的DEM数据和LUCC数据
#输出数据为重新分类的SLOPE/ASPECT/LUCC数据
import os,sys
from osgeo import gdal
import subprocess


DEM_DIR = "/home/lan/data_pool/orange/immutable/DEM/DEM.tif"
datapath = "/home/lan/data_pool/orange/immttable-mid-result/result_LUCC2010.tif"
aspect_file = "/home/lan/data_pool/orange/immutable/aspect/aspect.tif"
slope_file = "/home/lan/data_pool/orange/immutable/slope/slope.tif"
result_aspect = "/home/lan/data_pool/orange/immutable/aspect/test_aspect.tif"
result_slope = "/home/lan/data_pool/orange/immttable-mid-result/2010.tif"

def calculate_slope(DEM):
    gdal.DEMProcessing(slope_file, DEM, 'slope')


def calculate_aspect(DEM):
    gdal.DEMProcessing(aspect_file, DEM, 'aspect')

subprocess.call(['gdalwarp','-t_srs', '+proj=utm +zone=50 +north +datum=WGS84','-tr','1000','1000','-r','bilinear',datapath,DEM_DIR])
slope=calculate_slope(DEM_DIR)
aspect = calculate_aspect(DEM_DIR)
#
subprocess.call(['gdal_calc.py','-A',aspect_file,'--outfile',result_aspect,'--calc=1*((A>=0)*(A<=22.5))+\
2*((A>22.5)*(A<=67.5))+3*((A>67.5)*(A<=112.5))+4*((A>112.5)*(A<=157.5))+5*((A>157.5)*(A<=202.5))+6*((A>202.5)*(A<=247.5))+\
7*((A>247.5)*(A<=292.5))+8*((A>292.5)*(A<=337.5))+9*((A>337.5)*(A<=360))'])

subprocess.call(['gdal_calc.py','-A',slope_file,'--outfile',result_slope,'--calc=1*((A>=0)*(A<=1.69))+\
2*((A>1.69)*(A<=4.81))+3*((A>4.81)*(A<=8.49))+4*((A>8.49)*(A<=12.45))+5*((A>12.45)*(A<=16.98))+6*((A>16.98)*(A<=22.35))+\
7*((A>22.35)*(A<=29.15))+8*((A>29.15)*(A<=38.76))+9*((A>38.76)*(A<=90))'])

subprocess.call(['gdal_calc.py','-A',datapath,'--outfile',result_lucc,'--calc=1*((A>=10)*(A<=14))+\
1*(A==19)+ 1*(A==94)+2*((A>=20)*(A<=24))+2*(A==29)+3*((A>=30)*(A<=32))+3*(A==34)+3*(A==39)+3*(A==51)+3*(A==72)+\
4*(A==40)+4*(A==49)+4*(A==71)'])
