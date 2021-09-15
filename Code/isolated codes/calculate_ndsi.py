from osgeo import gdal, gdal_array
from osgeo import ogr
import functions as f

bands = ['B3','B6']

input_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/'
output_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/NDSI/'

rasterfile1 = input_folder + bands[0] + "/" + bands[0] + ".TIF"
rasterfile2 = input_folder + bands[1] + "/" + bands[1] + ".TIF"
ndsi_filename = output_folder + "/NDSI.TIF"

try:
    f.calculate_ndsi(rasterfile1, rasterfile2, ndsi_filename)
except:
    print("Error")


# glaciers = list(range(1,357))
# glaciers  = ["Number_" + str(s) for s in glaciers]

# input_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/'
# output_folder = '/Users/christianlannefranque/Google Drive USM/Thesis_Data/Satellite Scenes/13FEB15/AtacamaRegion/NDSI/'

# for glacier in glaciers:
#     rasterfile1 = input_folder + bands[0] + "/" + bands[0] + "_Buffer_0_" + glacier + ".tif"
#     rasterfile2 = input_folder + bands[1] + "/" + bands[1] + "_Buffer_0_" + glacier + ".tif"
#     ndsi_filename = output_folder + "Buffer_0_" + glacier + ".TIF"
#     # print(rasterfile1)
#     # print(rasterfile2)
#     # print(ndsi_filename)
#     try:
#         f.calculate_ndsi(rasterfile1, rasterfile2, ndsi_filename)
#     except:
#         print("Error, glacier: " + glacier)
