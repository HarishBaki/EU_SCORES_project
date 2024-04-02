import xarray as xr
import numpy as np
import sys, os
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import mean_statistics, std_statistics, quantile_statistics 

if __name__ == '__main__':
    region = sys.argv[1]
    file_name = sys.argv[2]
    variable = sys.argv[3]
    n_workers = int(sys.argv[4])

	# Create a Dask cluster
    print("Starting parallel computing...")
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=n_workers)
    # Connect to the cluster
    client = dd.Client(cluster)

    chunks={"time": -1,"y": 8,"x": 8}

    run_dir=f'{root_dir}/CERRA/{region}/variablewise_files'
    target_dir=f'{root_dir}/CERRA/{region}/statistics_files/{file_name}'
    os.makedirs(target_dir,exist_ok=True)

    ds = xr.open_dataset(f'{run_dir}/{file_name}.nc',chunks=chunks)
    if 'variable' in ds:
        ds = ds.drop('variable')
    data = ds[variable].isel(time=slice(None,-1),variable=0)

    # === mean ===#
    print('Calculating mean statistics')
    mean_statistics(data,time_coord='time').to_netcdf(f'{target_dir}/mean.nc')

    # === std ===#
    print('Calculating std statistics')
    std_statistics(data,time_coord='time').to_netcdf(f'{target_dir}/std.nc')

    # === CoV ===#
    print('Calculating CoV statistics')
    std = xr.open_dataset(f'{target_dir}/std.nc')
    mean = xr.open_dataset(f'{target_dir}/mean.nc')
    cov = (std/mean)
    cov.to_netcdf(f'{target_dir}/cov.nc')

    # === 5th quantile ===#
    print('Calculating 5th quantile statistics')
    quantile_statistics(data,0.05,time_coord='time').to_netcdf(f'{target_dir}/quantile_5.nc')

    # === 95th quantile ===#
    print('Calculating 95th quantile statistics')
    quantile_statistics(data,0.95,time_coord='time').to_netcdf(f'{target_dir}/quantile_95.nc')

    # === 99th quantile ===#
    print('Calculating 99th quantile statistics')
    quantile_statistics(data,0.99,time_coord='time').to_netcdf(f'{target_dir}/quantile_99.nc')
    
    client.close()
    cluster.close()
