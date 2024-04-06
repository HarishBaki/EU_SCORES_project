import xarray as xr
import numpy as np
import sys, os, glob
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import solar_power

if __name__ == "__main__":
    region = sys.argv[1]

    Epv = 0.216
    chunks={"time": 3600,"x": -1,"y": -1}
    run_dir = f'{root_dir}/CERRA/{region}/variablewise_files'

    ws = xr.open_dataset(f'{run_dir}/ws_10.nc',chunks=chunks)['ws']
    t2m = xr.open_dataset(f'{run_dir}/t2m.nc',chunks=chunks)['t2m']
    swdown = xr.open_dataset(f'{run_dir}/swdown.nc',chunks=chunks)['ssrd']

    spv = solar_power(ws, swdown,t2m, Epv)
    latitude = xr.open_dataset(f'{run_dir}/latitude.nc')
    longitude = xr.open_dataset(f'{run_dir}/longitude.nc')
    spv = spv.assign_coords(latitude=latitude['latitude'],longitude=longitude['longitude'])

    target_file = f'{run_dir}/spv.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    spv.to_netcdf(target_file,mode='w')
    print(f'Solar Power for {region} is extracted and saved')