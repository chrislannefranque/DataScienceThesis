from osgeo import gdal, gdal_array
import os
import geopandas as gpd
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
#from geopandas import gdal_merge as gm
import subprocess

buffers = ['Buffer_0']
glaciers = list(range(1,2))
glaciers  = ["Number_" + str(s) for s in glaciers]
print(glaciers)

#Get list of images to mosaic
directories = ['/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/','/Users/christianlannefranque/Google Drive USM/Thesis_Data/DEM/ASTER/ASTER_32619_ALIGNED/AtacamaRegion/ASTER/']
#directories = ['/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/']
output_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/All_bands/'

with tqdm(total=len(glaciers)*len(buffers)) as pbar:
  for buffer in buffers:
    for glacier in glaciers:

      output_image = output_folder + buffer + '/' + buffer + '_' + glacier + '.TIF'
      list_images = []

      for directory in directories:
        for subdir, dirs, files in os.walk(directory):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".tif") or filepath.endswith(".TIF"):
                  if glacier+'.tif' in filepath and buffer in filepath:
                    list_images.append(filepath)

      #print(list_images)
      parameters = ['', '-o', output_image,'-separate'] #remove separate if no need to put files in different bands
      #parameters = ['python3', 'gdal_merge.py', '-o', output_image, '-separate'] #remove separate if no need to put files in different bands
      parameters.extend(list_images)
      try:
        #print(parameters)
        gm.main(parameters)
        #merge_command = ["python", "gdal_merge.py", "-o", "output.tif", "input1.tif", "input2.tif", "input3.tif", "inputN.tif"]
        #subprocess.call(parameters)

      except:
        print("Error in " + buffer + " " + glacier)
      pbar.update(1)