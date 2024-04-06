import xarray as xr
import numpy as np
import sys, os, glob
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import wind_power_density, turbine_power

if __name__ == "__main__":
    region = sys.argv[1]
    
    chunks={"time": 3600,"x": -1,"y": -1}
    run_dir = f'{root_dir}/CERRA/{region}/variablewise_files'

    # ws 10 
    var = 'ws'
    level = '10'
    file_name = f'{run_dir}/{var}_{level}.nc'
    with xr.open_dataset(file_name,chunks=chunks) as ds:
        data = ds.drop('variable').sel(variable=0).load()
    # save the ds to the same file
    data.to_netcdf(file_name,mode='w')
    print(f'Wind speed for {region} {level} is extracted and saved')

    # ws 100
    var = 'ws'
    level = '100'
    file_name = f'{run_dir}/{var}_{level}.nc'
    with xr.open_dataset(file_name,chunks=chunks) as ds:
        data = ds.drop('variable').sel(variable=0).load()
    # save the ds to the same file
    data.to_netcdf(file_name,mode='w')
    print(f'Wind speed for {region} {level} is extracted and saved')
    
    # t2m, convert also to celcius
    var = 't2m'
    file_name = f'{run_dir}/{var}.nc'
    with xr.open_dataset(file_name,chunks=chunks) as ds:
        data = ds.drop('variable').sel(variable=0).load()
        # convert to celcius
        data = data - 273.15
    # save the ds to the same file
    data.to_netcdf(file_name,mode='w')
    print(f'Temperature for {region} is extracted and saved')

    # swdown, convert also into W/m^2
    var = 'swdown'
    file_name = f'{run_dir}/{var}.nc'
    with xr.open_dataset(file_name,chunks=chunks) as ds:
        data = ds.drop('variable').sel(variable=0).load()
    # convert to W/m^2
    data = data/3600
    # save the ds to the same file
    data.to_netcdf(file_name,mode='w')
    print(f'Downward shortwave radiation for {region} is extracted and saved')

