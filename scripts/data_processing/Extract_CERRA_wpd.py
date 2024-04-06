import xarray as xr
import numpy as np
import sys, os, glob
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import wind_power_density

if __name__ == "__main__":
    region = sys.argv[1]
    var = sys.argv[2]
    level = sys.argv[3]

    chunks={"time": 3600,"x": -1,"y": -1}
    run_dir = f'{root_dir}/CERRA/{region}/variablewise_files'
    ds = xr.open_dataset(f'{run_dir}/{var}_{level}.nc',chunks=chunks)
    data = ds

    rho = 1.225
    wpd = wind_power_density(data['ws'],rho)

    target_file = f'{run_dir}/wpd_{level}.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    wpd.to_netcdf(target_file,mode='w')
    print(f'Wind Power Density for {region} is extracted and saved')