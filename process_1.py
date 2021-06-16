from osgeo import gdal, gdal_array, osr
import ogr
import os
import geopandas as gpd
import numpy as np
from jdcal import gcal2jd, jd2gcal
import sys
import time
import multiprocessing

"""##Local Parameters"""

#change this to where ever the process file is
path_to_input_files = "/Users/christianlannefranque/Desktop/"
path_to_development_files = "/Users/christianlannefranque/Desktop/"
path_to_output_files = "/Users/christianlannefranque/Desktop/"

## 2) Extract

Rasterfile = path_to_input_files+"input_mosaic.tiff"
print(Rasterfile)
outputRaster = path_to_output_files + "output.tif"
reprojected_shapefile = path_to_development_files + "Cryosphere/criosfera_atacama_fixed_geometry_reprojected.shp"
rlayer = gdal.Open(Rasterfile, gdal.GA_ReadOnly)
kwargs={'cutlineDSName' : reprojected_shapefile,'cropToCutline' : True}
gdal.Warp(outputRaster,rlayer,**kwargs)