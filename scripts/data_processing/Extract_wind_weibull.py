import xarray as xr
import numpy as np
import sys, os
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import weibull, weibull_statistics

if __name__ == '__main__':
    run = sys.argv[1]
    case = sys.argv[2]
    level = int(sys.argv[3])
    i = int(sys.argv[4])
    j = int(sys.argv[5])
    time_scale = sys.argv[6]

    run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
    target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/statistics_files/ws_{level}'

    os.makedirs(f'{target_dir}/weibull',exist_ok=True)

    chunks={"Time": -1,"south_north": 1,"west_east": 1}
    ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']

    # remove if file exist
    target_file = f'{target_dir}/weibull/{i}_{j}.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    # Calculate weibull statistics

    weibull_statistics(ws, i, j, time_scale).to_netcdf(target_file)
