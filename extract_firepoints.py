# -*- coding: utf-8 -*-
#输入数据为VIIRS750的异常点文件
#输出为研究区范围内的火点数据


import netCDF4, arrow, pprint
import pdb
import pandas as pd
from os.path import join
import glob
import utm
class Extractor():
    def __init__(self):
        pass

    def extract_fire_location(self, file_path):
        self.dataset = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        coordinates = self._read_coordinates()
        metadata = self._read_metadata()
        result = {'meta': metadata, 'coordinates': coordinates}
        return result

    def _read_coordinates(self):
        coordinates = []
        fire_pixel_count = self.dataset.FirePix
        if fire_pixel_count > 0:
            for pixel_index in range(0,fire_pixel_count):
                #Lat and Long in the range of (-90, 90), (-180, 180) respectively, in WGS84
                latitude = self.dataset.variables['FP_latitude'][pixel_index]
                longitude = self.dataset.variables['FP_longitude'][pixel_index]
                lon_center = utm.from_latlon(latitude,longitude)[0]
                lat_center = utm.from_latlon(latitude,longitude)[1]
                #calculate the positions of the four corners
                lon_left = lon_center - 375
                lon_right = lon_center + 375
                lat_upper = lat_center + 375
                lat_lower = lat_center - 375
                #Confidence level in the range of [1, 100]
                confidence = self.dataset.variables['FP_confidence'][pixel_index]
                date = self.dataset.LocalGranuleID.split(".")[1]
                new_date = date[1:8]
                # print(new_date)
                if (latitude < 37) and(latitude > 29.5) and (longitude < 120.6) and (longitude > 110):
                    coordinates.append((lon_left, lat_upper, confidence,new_date))
                    coordinates.append((lon_right, lat_upper, confidence,new_date))
                    coordinates.append((lon_right, lat_lower, confidence,new_date))
                    coordinates.append((lon_left, lat_lower, confidence,new_date))
        return coordinates

    def _read_metadata(self):
        begin_timestamp = arrow.get(self.dataset.RangeBeginningDate+' '+self.dataset.RangeBeginningTime).timestamp
        end_timestamp = arrow.get(self.dataset.RangeEndingDate+' '+self.dataset.RangeEndingTime).timestamp
        production_time = arrow.get(self.dataset.ProductionTime).timestamp
        return {'begin_timestamp': begin_timestamp, 'end_timestamp': end_timestamp, 'production_time': production_time}
# printer = pprint.PrettyPrinter(indent=3)
# printer.pprint(result)

fire_folder = "/home/lan/data_pool/orange/fire_point"
firefile_list = glob.glob(join(fire_folder,"*","*.nc"))
firefile_list.sort()
# printer.pprint(firefile_list)
result = {'meta':[],'coordinates':[]}
for filee in firefile_list:
    e = Extractor()
    midresult = e.extract_fire_location(filee)
    result['coordinates'] = result['coordinates']+ midresult['coordinates']
    print(filee + " is processed!")
dataset = pd.DataFrame(result['coordinates'])
print(dataset)
dataset.to_csv("/home/lan/data_pool/orange/fire_point/fire_points.csv")
