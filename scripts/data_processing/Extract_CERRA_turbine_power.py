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
    root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
    
    region = sys.argv[1]
    var = sys.argv[2]
    level = sys.argv[3]
    turbine_type = str(sys.argv[4])
    
    chunks={"time": 3600,"x": -1,"y": -1}
    run_dir = f'{root_dir}/CERRA/{region}/variablewise_files'
    ds = xr.open_dataset(f'{run_dir}/{var}_{level}.nc',chunks=chunks)
    data = ds

    tp = turbine_power(data['ws'],turbine_type=turbine_type)
    
    # save to file
    if not os.path.exists(f'{run_dir}/{turbine_type}'):
        os.makedirs(f'{run_dir}/{turbine_type}')
    target_file = f'{run_dir}/{turbine_type}/tp_{level}.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    tp.to_netcdf(target_file)
    print(f'Turbine power for {region} {turbine_type} {level} is extracted and saved')
