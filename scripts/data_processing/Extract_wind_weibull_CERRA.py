import xarray as xr
import numpy as np
import sys, os, glob
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import mean_statistics, std_statistics, wind_power_density, weibull , weibull_statistics

region = sys.argv[1]
level = int(sys.argv[2])
i = int(sys.argv[3])
j = int(sys.argv[4])

if __name__ == '__main__':
    start = time.time()
    run_dir = f'{root_dir}/CERRA'
    chunks={"time": -1,"x": 1,"y": 1}
    ds = xr.open_dataset(f'{run_dir}/{region}/variablewise_files/ws_{level}.nc',chunks=chunks)
    ws = ds['ws'].isel(variable=0,time=slice(None,-1))

    # make dir if doesnt exist
    target_dir = f'{run_dir}/{region}/statistics_files/ws_{level}'
    os.makedirs(f'{target_dir}/weibull', exist_ok=True)

    # remove if file exist
    target_file = f'{target_dir}/weibull/{i}_{j}.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    # Calculate weibull statistics
    weibull_statistics(ws,i,j,time_coord='time',south_north='y',west_east='x').to_netcdf(target_file)
    print(f'{i}_{j} done in {time.time()-start} seconds')
