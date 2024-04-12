import xarray as xr
import numpy as np
import sys, os
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import mean_statistics, std_statistics, quantile_statistics, compute_statistics 

if __name__ == '__main__':
    region = sys.argv[1]
    file_name = sys.argv[2]
    variable = sys.argv[3]
    n_workers = int(sys.argv[4])
    dashboard_port = sys.argv[5]
    statistic = sys.argv[6]
    time_scale = sys.argv[7]

	# Create a Dask cluster
    print("Starting parallel computing...")
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=n_workers, threads_per_worker=2, memory_limit='2GB',dashboard_address=f':{dashboard_port}')
    # Connect to the cluster
    client = dd.Client(cluster)

    dim='time'
    chunks={f"{dim}": -1,"y": 8,"x": 8}

    run_dir=f'{root_dir}/CERRA/{region}/variablewise_files'
    target_dir=f'{root_dir}/CERRA/{region}/statistics_files/{file_name}'
    os.makedirs(target_dir,exist_ok=True)

    ds = xr.open_dataset(f'{run_dir}/{file_name}.nc',chunks=chunks)
    if 'variable' in ds:
        ds = ds.drop('variable')
    data = ds[variable].isel(time=slice(None,-1))

    target_file = f'{target_dir}/{statistic}.nc'
    print(target_file)
    if os.path.exists(target_file):
        with xr.open_dataset(target_file) as target_ds:
            target_ds = target_ds.load()
    else:
        target_ds = xr.Dataset()

    # Check if the statistic contains an underscore
    if '_' in statistic:
        statistic,quantile = statistic.split('_')
        quantile = int(quantile)
        stat = compute_statistics(data, statistic, time_scale=time_scale,dim=dim,q=quantile/100)
    else:
        stat = compute_statistics(data, statistic, time_scale=time_scale,dim=dim)
    target_ds[f'{time_scale}_values'] = stat
    target_ds.to_netcdf(target_file)
    
    client.close()
    cluster.close()
