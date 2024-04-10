import xarray as xr
import numpy as np
import sys, os
import time

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

if __name__ == '__main__':
    run = sys.argv[1]
    case = sys.argv[2]
    file_name = sys.argv[3]
    variable = sys.argv[4]

    run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
    target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/statistics_files/{file_name}'

    mean_ds = xr.open_dataset(f'{target_dir}/mean.nc')
    std_ds = xr.open_dataset(f'{target_dir}/std.nc')

    # read the target dataset if it exists
    statistic = 'cov'
    target_file = f'{target_dir}/{statistic}.nc'
    if os.path.exists(target_file):
        with xr.open_dataset(target_file) as target_ds:
            target_ds = target_ds.load()
    else:
        target_ds = xr.Dataset()
    target_ds = (std_ds)/(mean_ds) 
    
    target_ds.to_netcdf(target_file,mode='w')