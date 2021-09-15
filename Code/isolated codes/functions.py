from osgeo import gdal, gdal_array
from osgeo import ogr
import numpy as np
import pandas as pd

def calculate_ndsi(rasterfile1,rasterfile2, ndsi_filename):

  #inputs:
  #rasterfile1: first raster file
  #rasterfile2: second raster file
  
  #considerations:
  #both raster files have the same size.
  #both raster files have the same driver.
  
  #read raster files
  rlayer1 = gdal.Open(rasterfile1, gdal.GA_ReadOnly)
  rlayer2 = gdal.Open(rasterfile2, gdal.GA_ReadOnly)

  #get # columns and rows and bands
  cols = rlayer1.RasterXSize
  rows = rlayer1.RasterYSize

  #get georeference & projection
  geoTransform = rlayer1.GetGeoTransform()
  proj = rlayer1.GetProjection()
  
  #bands = rlayer1.RasterCount

  #read first band
  band1 = rlayer1.GetRasterBand(1)
  band2 = rlayer2.GetRasterBand(1)

  #get numpy array
  array1 = band1.ReadAsArray(0, 0, cols, rows)
  array2 = band2.ReadAsArray(0, 0, cols, rows)

  #Set no data value to nan
  array1 = np.where(array1 == array1.min(), np.nan, array1)
  array2 = np.where(array2 == array2.min(), np.nan, array2)

  #calculate ndsi
  ndsi = (array1-array2)/(array1+array2)

  #get driver to write
  driver = rlayer1.GetDriver()

  #create output raster
  outDataset = driver.Create(ndsi_filename, cols, rows, 1, gdal.GDT_Float32)
  outDataset.SetGeoTransform(geoTransform)
  outDataset.SetProjection(proj)

  # get band for out dataset
  outBand = outDataset.GetRasterBand(1)

  #write ndsi
  outBand.WriteArray(ndsi, 0, 0)

  #set all to null for memory purposes
  rlayer1 = None
  rlayer2 = None
  geoTransform = None
  band1 = None
  band2 = None
  array1 = None
  array2 = None
  ndsi = None
  driver = None
  outDataset = None
  outBand = None

def shapefile_data_to_df(shapefile):
  driver = ogr.GetDriverByName('ESRI Shapefile')
  dataset = driver.Open(shapefile)
  layer = dataset.GetLayer()
  layer.ResetReading() #need if looping again
  feature = layer.GetNextFeature()

  i=0

  while feature:

    df1 = pd.DataFrame(feature.items(), index=[i])
    
    if i == 0:
      df2 = df1
    
    else:
      df2 = df2.append(df1)
    
    i = i+1
    feature = layer.GetNextFeature()

  #df2.reset_index(inplace=True)
  
  driver = None
  dataset = None
  layer = None
  feature = None

  return df2

def shapefile_data_to_csv(shapefile):
  df = shapefile_data_to_df(shapefile)
  csv_file = shapefile.rsplit(sep=".",maxsplit=1)[0]
  csv_file = csv_file + '.csv'
  df.to_csv(csv_file)
  return 1

def extract_by_extent(rasterfile,shapefile,output):
  rasterlayer = gdal.Open(rasterfile, gdal.GA_ReadOnly)
  
  driver = ogr.GetDriverByName('ESRI Shapefile')
  dataset = driver.Open(shapefile)
  layer = dataset.GetLayer()
  extent = layer.GetExtent()

  result = gdal.Translate(output, rasterlayer, projWin = [extent[0], extent[3], extent[1], extent[2]])
  
  driver = None
  rasterlayer = None
  dataset = None
  layer = None
  output = None
  result = None

  return 1

def extract_by_extent_fixed(rasterfile,shapefile,output,x,y):
  
  rasterlayer = gdal.Open(rasterfile, gdal.GA_ReadOnly)
  
  gt = rasterlayer.GetGeoTransform()
  pixelSizeX = gt[1]
  pixelSizeY = -gt[5]

  driver = ogr.GetDriverByName('ESRI Shapefile')
  dataset = driver.Open(shapefile)
  layer = dataset.GetLayer()
  extent = layer.GetExtent()

  ulx = extent[0]
  uly = extent[3]
  lrx = extent[1]
  lry = extent[2]

  ulx_new = ulx - ((x*pixelSizeX - (lrx - ulx)) / 2)
  lrx_new = lrx + ((x*pixelSizeX - (lrx - ulx)) / 2)
  uly_new = uly + ((y*pixelSizeY - (uly - lry)) / 2)
  lry_new = lry - ((y*pixelSizeY - (uly - lry)) / 2)

  result = gdal.Translate(output, rasterlayer, projWin = [ulx_new, uly_new, lrx_new, lry_new])
  
  driver = None
  rasterlayer = None
  dataset = None
  layer = None
  output = None
  result = None

  return 1

def extract_by_mask(rasterfile,shapefile,output):
  rasterlayer = gdal.Open(rasterfile, gdal.GA_ReadOnly)
  
  cols = rasterlayer.RasterXSize
  rows = rasterlayer.RasterYSize
  
  kwargs={'cutlineDSName':shapefile, 'width':cols, 'height':rows,'cropToCutline':False}
  result = gdal.Warp(output,rasterlayer,**kwargs)

  rasterlayer = None
  cols = None
  rows = None
  output = None

  return result

def mask_calculator(a, b):
    #a = pixel value in mask1
    #b = pixel value in mask2
    
    #examples
    #1) pixel in main glacier --> a > 0 and b > 0
    #2) pixel in surrounding glacier --> a > 1 and b = 0
    #3) non - ice pixel --> a = 0

    # non-ice pixel
    if a == 0:
        return 0
    
    
    else:
      # surrounding glacier
      if b == 0:
        return 2
      # main glacier
      else:
        return 1

vectorize_mask_function = np.vectorize(mask_calculator)

def mask_calculator_2d(mask0, mask1, mask2):

    # print(mask0[-1,-1])
    # print(mask1[-1,-1])
    # print(mask2[-1,-1])

    #mask0 = only values for main glacier + surrounding glacier + non_glacier + argentina (with negative values)
    mask0 = np.where(mask0 >= 0, 1, 0) # main glacier, surrounding glacier and non glacier = 1 and argentina = 0

    #mask1 = only values for main glacier + surrounding glacier
    mask1 = np.where(mask1 >= 0, 1, 0) # main glacier and surrounding glacier = 1, the rest = 0

    #mask2 = only values for main glacier
    mask2 = np.where(mask2 >= 0, 1, 0) # main glacier = 1, the rest = 0
    
    #mask3 = sum of mask0, mask1 and mask2 then
    mask3 = mask0 + mask1 + mask2 #main glacier = 3, surrounding glacier = 2, non glacier = 1, argentina = 0
    
    #2 classes mask: (comment next line if you need 3 classes mask)
    mask3 = np.where(mask3 > 1, 1, 0)
    
    # mask3 = np.where(mask3 == 1, 3, mask3) #sg to 3
    # mask3 = np.where(mask3 == 2, 1, mask3) #mg to 1
    # mask3 = np.where(mask3 == 3, 2, mask3) #sg to 2

    return mask3

def calculate_mask(rasterfile0, rasterfile1,rasterfile2, mask_output):

  #inputs:
  #rasterfile1: first raster file
  #rasterfile2: second raster file
  
  #considerations:
  #both raster files have the same size.
  #both raster files have the same driver.

  rlayer1 = gdal.Open(rasterfile1, gdal.GA_ReadOnly)
  cols = rlayer1.RasterXSize
  rows = rlayer1.RasterYSize
  band1 = rlayer1.GetRasterBand(1)
  array1 = band1.ReadAsArray(0, 0, 120, 120)
  
  rlayer2 = gdal.Open(rasterfile2, gdal.GA_ReadOnly)
  band2 = rlayer2.GetRasterBand(1)
  array2 = band2.ReadAsArray(0, 0, 120, 120)
  
  rlayer0 = gdal.Open(rasterfile0, gdal.GA_ReadOnly)
  band0 = rlayer0.GetRasterBand(1)
  array0 = band0.ReadAsArray(0, 0, 120, 120)
  
  #print(array1.sum(),array2.sum())

  #get Geo data
  geoTransform = rlayer1.GetGeoTransform()
  proj = rlayer1.GetProjection()
  
  #get driver to write
  driver = rlayer1.GetDriver()

  #calculate mask
  #mask = vectorize_mask_function(array1, array2)
  mask = mask_calculator_2d(array0, array1, array2)

  # #create output raster
  outDataset = driver.Create(mask_output, cols, rows, 1, gdal.GDT_Float32)
  outDataset.SetGeoTransform(geoTransform)
  outDataset.SetProjection(proj)

  # # get band for out dataset
  outBand = outDataset.GetRasterBand(1)

  # #write ndsi
  outBand.WriteArray(mask, 0, 0)

  #set all to null for memory purposes
  rlayer1 = None
  band1 = None
  array1 = None
  rlayer2 = None
  band2 = None
  array2 = None
  driver = None
  outDataset = None
  outBand = None

  return 1

def glacier_vector(rasterfile):
  
  #get the number of the main glacier
  number = rasterfile.rsplit(".")[0]
  number = number.rsplit("/")[-1]
  number = number.rsplit("_")[-1]
  number = int(number)

  #read raster, band and array
  rasterlayer = gdal.Open(rasterfile, gdal.GA_ReadOnly)
  band = rasterlayer.GetRasterBand(1)
  array = band.ReadAsArray(0, 0, 120, 120)

  #get uniquie values from array
  values = np.unique(array)
  #filter no data values (-99999), positive values and the main glacier
  values = values[(values < 0) & (values != -99999) & (values != -number)]
  #change to positive values
  values = values * -1
  #Add values 
  values = np.append([number],values)

  return values

def glacier_vector2(rasterfile):
  
  #get the number of the main glacier
  number = rasterfile.rsplit(".")[0]
  number = number.rsplit("/")[-1]
  number = number.rsplit("_")[-1]
  number = int(number)

  #read raster, band and array
  rasterlayer = gdal.Open(rasterfile, gdal.GA_ReadOnly)
  band = rasterlayer.GetRasterBand(1)
  array = band.ReadAsArray(0, 0, 120, 120)

  #get uniquie values from array
  values, counts = np.unique(array, return_counts=True)
  #filter no data values (-99999), positive values and the main glacier
  bool_array = [(values < 0) & (values != -99999)]# & (values != -number)]
  values = values[tuple(bool_array)]
  counts = counts[tuple(bool_array)]

  #change to positive values
  values = values.astype(int) * -1

  #put everything in dictionary
  d = {}
  for value, count in zip(values, counts):
      d[value] = count

  #move main glacier to first position
  main_glacier_dict = {number: d.pop(number)}
  main_glacier_dict.update(d)

  #make final dictionary
  dic = {number:main_glacier_dict}
  return dic

def remove_glacier_in_vectors(glaciers_dict:dict, remove_glacier:int):
  
  for main_glacier in list(glaciers_dict): #{54 :{54:10, 55:2}, 57:{57:3, 58:4} } -- list =  54 and 57  
    
    #get vector
    vector = glaciers_dict[main_glacier] # {54:10, 55:2}

    if remove_glacier in vector:
      glaciers_dict.pop(main_glacier)
  
  return glaciers_dict