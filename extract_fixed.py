from osgeo import gdal, gdal_array
from osgeo import ogr

#lists of bands, buffers and glaciers
bands = ['B1','B2','B3','B4','B5','B6','B7','B10']
buffers = ['Buffer_P15']
glaciers = list(range(1,357))
glaciers  = ["Number_" + str(s) for s in glaciers]
print(glaciers)

#location of files
bands_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/'
shapefiles_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/'


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

  return result


#rasterfile = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/B1/B1.TIF'
#shapefile = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/Buffer_0/split/Number_108.shp'
#output = '/Users/christianlannefranque/Desktop/B1_Buffer_0_Number_108_aux.TIF'

for band in bands:
  for buffer in buffers:
    for glacier in glaciers:
      
      #step 1
      rasterfile = bands_folder + band + '/' + band + '.TIF'
      #print(rasterfile)
      shapefile = shapefiles_folder + buffer + '/split/' + glacier + '.shp'
      #print(shapefile)
      output = bands_folder + band + '/' + band + '_' + buffer + '_' + glacier + '.tif'
      #shapefile_data_to_csv(shapefile)
      try:
        #result = extract_by_extent(rasterfile,shapefile,output)
        result = extract_by_extent_fixed(rasterfile,shapefile,output,120,120)
      except:
        print("Band " + band + "- Buffer " + buffer + "- Glacier " + glacier + ": Fail (1)")
        continue

      if result is None:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + ": Fail (2)")
      else:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + ": Success")