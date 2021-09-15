from osgeo import gdal, gdal_array
from osgeo import ogr
import functions as f
import os
import numpy as np
import pandas as pd

#lists of bands, buffers and glaciers
glaciers = list(range(1,357))
glaciers  = ["Number_" + str(s) for s in glaciers]
#print(glaciers)

#location of files
input_directory = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/B1_GN/'

# 1) build dictionary for each main glacier
all_glaciers = {}
for subdir, dirs, files in os.walk(input_directory):
    for filename in files:
        filepath = subdir + os.sep + filename
        if filepath.endswith(".tif") or filepath.endswith(".TIF"):
            if any(glacier+'.tif' in filepath for glacier in glaciers):        
                #get glacier vector with function
                glacier_vector = f.glacier_vector2(filepath)
                all_glaciers.update(glacier_vector)

print("Total:" + str(len(all_glaciers)))
#all_glaciers = {mg1 : {mg1:pixels, sg1:pixel2, sg2:pixels... }, mg2 : {mg2:pixels, sg1:pixels...} ... }


#2) get isolated vectors
isolated_glaciers = {}
for glacier,vector in all_glaciers.items():
    if len(vector) == 1:
        isolated_glaciers.update({glacier:vector})

print("Isolated:" + str(len(isolated_glaciers)))
#isolated_glaciers = {mg1 : {mg1:pixels}, mg2 : {mg2:pixels} ... }

#3) get non isolated glacier that don't contain the isolated glaciers
non_isolated_glaciers = {}
dropped_non_isolated_glaciers = {}

for glacier,vector in all_glaciers.items():
    if len(vector) > 1:
        if not any(isolated_glacier in vector for isolated_glacier in isolated_glaciers):
            non_isolated_glaciers.update({glacier:vector})
        else:
            dropped_non_isolated_glaciers.update({glacier:vector})

print("Non Isolated: " + str(len(non_isolated_glaciers)))
print("Non Isolated Dropped: " + str(len(dropped_non_isolated_glaciers)))

# 4) read shapefile csv file with areas of different glaciers
df_shapefile = pd.read_csv('/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/Buffer_0/Buffer_0.csv')
df_shapefile = df_shapefile[['Number','AREA']]

# 5) Get Square difference for each main glacier image
for main_glacier, vector in non_isolated_glaciers.items():
    
    #example main_glacier = 56
    #vector = {56:10, 57:11}

    #get surface pixel area
    sum_of_squared_dif = 0
    sum_pixel_area = 0 
    sum_shapefile_area = 0

    for glacier, pixels in vector.items():
        
        #glacier = 56
        #pixel = 10

        #pixel area km2
        pixel_area = 30/1000 * 30/1000 * pixels
        #real area from shapefile
        shapefile_area = df_shapefile[df_shapefile['Number'] == glacier]['AREA'].values[0]
        #get squared diference
        sq_dif = (pixel_area-shapefile_area)**2
        
        #sum
        sum_pixel_area = sum_pixel_area + pixel_area
        sum_shapefile_area = sum_shapefile_area + shapefile_area
        sum_of_squared_dif = sum_of_squared_dif + sq_dif

    data = {"main_glacier": [main_glacier], "sum_pixel_area":[sum_pixel_area], "sum_shapefile_area":[sum_shapefile_area], "sum_of_squared_dif":[sum_of_squared_dif]}
    
    try: 
        df_areas = df_areas.append(pd.DataFrame(data))
    except:
        df_areas = pd.DataFrame(data)

df_areas.reset_index(drop=True,inplace=True)
df_areas = df_areas.sort_values(by=['sum_of_squared_dif'], ascending=True)
#print(df_areas)

#6) Iterate over df_areas, selecting best main_glaciers
selected_non_isolated_glaciers = {}

for index, row in df_areas.iterrows():
    
    search_glacier = row['main_glacier'] #54
    
    #try to pop the searched glacier
    try:
        pop = non_isolated_glaciers.pop(search_glacier)

        #if we popped the searched glacier: 
        if pop:

            #we add it to the non_isolated_glaciers
            selected_non_isolated_glaciers.update({search_glacier:pop})
            
            #we have to remove all the images that include any of the surrounding glaciers or the main glacier
            for glacier, pixels in pop.items():
                non_isolated_glaciers = f.remove_glacier_in_vectors(non_isolated_glaciers, glacier)
    
    #Else, we remove all the images that include the searched glaciers
    except:
         non_isolated_glaciers = f.remove_glacier_in_vectors(non_isolated_glaciers, search_glacier)

print("Non Isolated Selected: " + str(len(selected_non_isolated_glaciers)))
#print("Non Isolated Dropped: " + str(len(dropped_non_isolated_glaciers)))

# glaciers_list = []
# for main_glacier, vector in selected_non_isolated_glaciers.items():
#     for glacier, pixel in vector.items():
#         glaciers_list.append(glacier)

# print(glaciers_list)

selected_images = {**isolated_glaciers, **selected_non_isolated_glaciers} 

#create dictionary of glaciers and it's corresponding main_glacier/image
selected_glaciers_image = {}
for main_glacier, vector in selected_images.items():
  for glacier, pixel in vector.items():
   selected_glaciers_image.update({glacier:main_glacier})
