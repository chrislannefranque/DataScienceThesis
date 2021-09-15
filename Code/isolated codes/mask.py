import os 
import numpy as np
import functions as f

#lists of bands, buffers and glaciers
bands = ['B1']
buffers = ['Buffer_0','Buffer_P15']
glaciers = list(range(0,357))
glaciers  = ["Number_" + str(s) for s in glaciers]
print(glaciers)

#location of files
bands_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/'
shapefiles_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/'
output_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/Mask/2 Classes/'
current_folder = os.path.dirname(os.path.realpath(__file__))

temp_file = current_folder + '/temp.tif'
temp_file2 = current_folder + '/temp2.tif'


for band in bands: 
  for buffer in buffers:
    #step 2.1
    rasterfile = bands_folder + band + '/' + band + '.TIF'
    shapefile_ug = shapefiles_folder + buffer + '/' + buffer + '.shp'
    
    try:
      result = f.extract_by_mask(rasterfile,shapefile_ug,temp_file)
    except:
      print(rasterfile)
      print(shapefile_ug)
      print("Band " + band + " - Buffer " + buffer + " - Step 2.1: Fail (1)")
      continue
    
    if result is None:
      print("Band " + band + " - Buffer " + buffer + " - Step 2.1: Fail (2)")
    else:
      print("Band " + band + " - Buffer " + buffer + " - Step 2.1: Success")  
  
    for glacier in glaciers:
      
      #step 2.2
      shapefile = shapefiles_folder + buffer + '/split/' + glacier + '.shp'
      mask1 = bands_folder + band + '/' + band + '_' + buffer + '_' + glacier + '_Mask1.tif'
      
      try:
        result = f.extract_by_extent_fixed(temp_file, shapefile, mask1, 120, 120)
      except:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 2.2: Fail (1)")
        continue
      
      if result is None:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 2.2: Fail (2)")
      else:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 2.2: Success")

      #step 3.1
      try:
        result = f.extract_by_mask(rasterfile, shapefile, temp_file2)
      except:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.1: Fail (1)")
        continue
      if result is None:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.1: Fail (2)")
      else:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.1: Success")

      #step 3.2
      mask2 = bands_folder + band + '/' + band + '_' + buffer + '_' + glacier + '_Mask2.tif'
      try:
        result = f.extract_by_extent_fixed(temp_file2,shapefile, mask2, 120, 120)
      except:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.2: Fail (1)")
        continue

      if result is None:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.2: Fail (2)")
      else:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 3.2: Success")

      os.remove(temp_file2)

      #step 4
      #mask3 = bands_folder + band + '/' + band + '_' + buffer + '_' + glacier + '_Mask3.tif'
      output_mask = output_folder + buffer + '/' + buffer + '_' + glacier + '_Mask.tif'
      
      try:
        #print(mask1,mask2,output_mask)
        raw_glacier = bands_folder + band + '/' + band + '_' + buffer + '_' + glacier + '.tif'
        #print(raw_glacier)
        result = f.calculate_mask(raw_glacier, mask1, mask2, output_mask)
      except:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 4: Fail (1)")
        continue
      
      if result == 1:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 4: Success")
      else:
        print("Band " + band + " - Buffer " + buffer + " - Glacier " + glacier + " - Step 4: Fail (2)")
      
      os.remove(mask1)
      os.remove(mask2)

    os.remove(temp_file)
    rasterfile = None