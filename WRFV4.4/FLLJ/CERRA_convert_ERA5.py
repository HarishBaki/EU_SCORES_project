# conda activate wrf-python-stable
import pygrib
import numpy as np

# certifiate verification
import certifi
import urllib3


# This function takes input arguments through command lines 
# argv[1] = cdsapirc file name, which could be either '/home/harish/.cdsapirc2' or another
# argv[2] = x_year
# argv[3] = x_month
# argv[4] = x_day
# argv[5] = x_time

import sys
year = sys.argv[2]
month = sys.argv[3]
day = sys.argv[4]
time = sys.argv[5] # convert time into two digit format

# if time is divisible by 3, then product_type = "analysis", else product_type = "forecast
if int(time)%3 == 0:
    product_type = "analysis"
    hour = int(time)
    print(year,month,day,time,product_type, hour)

else:
    product_type = "forecast"
    # convert time into nearest multiple of 3
    leadtime_hour = int(time)%3
    hour = str(int(int(time)/3)*3)
    print(year,month,day,time,product_type,hour, leadtime_hour)

#--- Change values of year, month, day, and time only ---#

# Import cdsapi and create a Client instance
import cdsapi

import yaml
cdsapirc_file = sys.argv[1]
with open(cdsapirc_file, 'r') as f:
	credentials = yaml.safe_load(f)
c = cdsapi.Client(url=credentials['url'], key=credentials['key'])
#

c.retrieve("reanalysis-cerra-pressure-levels", {
        "data_type": "reanalysis",
        "product_type": product_type,
        "variable":       ["u","v","z","t","r"],
        "pressure_level": ["1","2","3","5","7","10","20","30","50","70","100",
                           "125","150","175","200","225","250","300","350","400",
                           "450","500","550","600","650","700","750","775","800",
                           "825","850","875","900","925","950","975","1000"],
        "year":           year,
        "month":          month,
        "day":            day,
        "time":           hour,
        # if product_type == "forecast", then add leadtime_hour
        **({"leadtime_hour": leadtime_hour} if product_type == "forecast" else {}),
        "format":          "grib",
    }, "CERRA_"+year+"_"+month+"_"+day+"-"+time+"_PRES.grb")
print("CERRA_"+year+"_"+month+"_"+day+"-"+time+"_PRES.grb")

c.retrieve("reanalysis-cerra-single-levels", {
        "data_type": "reanalysis",
        "product_type": product_type,
        "level_type": "surface_or_atmosphere",
        'variable': [
        '10m_wind_direction', '10m_wind_speed', '2m_relative_humidity',
        '2m_temperature', 'albedo', 'high_cloud_cover',
        'land_sea_mask', 'low_cloud_cover', 'mean_sea_level_pressure',
        'medium_cloud_cover', 'orography', 'skin_temperature',
        'snow_density', 'snow_depth', 'snow_depth_water_equivalent',
        'surface_pressure', 'surface_roughness', 'total_cloud_cover',
        'total_column_integrated_water_vapour'],
        "year":           year,
        "month":          month,
        "day":            day,
        "time":           hour,
        # if product_type == "forecast", then add leadtime_hour
        **({"leadtime_hour": leadtime_hour} if product_type == "forecast" else {}),
        "format":          "grib",
    }, "CERRA_"+year+"_"+month+"_"+day+"-"+time+"_SFC.grb")
print("CERRA_"+year+"_"+month+"_"+day+"-"+time+"_SFC.grb")

grbs = pygrib.open("CERRA_"+year+"_"+month+"_"+day+"-"+time+"_SFC.grb")
grbout = open("CERRA_"+year+"_"+month+"_"+day+"-"+time+"_U10_V10.grb",'wb')
variable_names = ['10 metre wind speed','10 metre wind direction']
for grb1,grb2 in zip(grbs.select(name=variable_names[0]),grbs.select(name=variable_names[1])): #why in combination? Because, grib reads line wise, which means, one data point at a time.
    print(grb1,grb2)
    wspd = grb1.values
    wdir_deg = np.radians(grb2.values)
    U10 = -grb1.values*np.sin(wdir_deg)
    V10 = -grb1.values*np.cos(wdir_deg)

    grb_U10 = grb1
    grb_U10.values = U10
    grb_U10.paramId = 165
    pygrib.reload(grb_U10)
    msg = grb_U10.tostring()
    grbout.write(msg)

    grb_V10 = grb2
    grb_V10.values = V10
    grb_V10.paramId = 166
    pygrib.reload(grb_V10)
    msg = grb_V10.tostring()
    grbout.write(msg)
grbs.close()
grbout.close()
print("CERRA_"+year+"_"+month+"_"+day+"-"+time+"_U10_V10.grb")

c.retrieve("reanalysis-era5-single-levels", {
    "product_type":   "reanalysis",
    "area":           "60.00/-20.00/40.00/20.00",
    "variable":       ["stl1","stl2","stl3","stl4","slt","swvl1","swvl2","swvl3","swvl4"],
    "year":           year,
    "month":          month,
    "day":            day,
    "time":           time,
}, "ERA5_"+year+"_"+month+"_"+day+"-"+time+"_soil.grb")
print("ERA5_"+year+"_"+month+"_"+day+"-"+time+"_soil.grb")