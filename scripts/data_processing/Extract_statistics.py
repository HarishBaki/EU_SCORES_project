import xarray as xr
import numpy as np
import sys, os
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import mean_statistics, std_statistics, quantile_statistics ,compute_statistics

if __name__ == '__main__':
    run = sys.argv[1]
    case = sys.argv[2]
    file_name = sys.argv[3]
    variable = sys.argv[4]
    n_workers = int(sys.argv[5])
    dashboard_port = sys.argv[6]
    statistic = sys.argv[7]
    time_scale = sys.argv[8]

	# Create a Dask cluster
    print("Starting parallel computing...")
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=n_workers,threads_per_worker=2,memory_limit='2GB',dashboard_address=f':{dashboard_port}')
    # Connect to the cluster
    client = dd.Client(cluster)
    print(client)

    dim='Time'
    chunks={f"{dim}": -1,"south_north": 8,"west_east": 8}

    run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
    target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/statistics_files/{file_name}'

    source_ds = xr.open_dataset(f'{run_dir}/{file_name}.nc',chunks=chunks)[variable]
    data = source_ds.isel({f'{dim}': slice(None,-1)})

    XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc').load()
    XLAT = XLAND.XLAT
    XLONG = XLAND.XLONG

    if 'XLAT' not in data.coords or 'XLONG' not in data.coords:
        data = data.assign_coords(XLAT=XLAT, XLONG=XLONG)

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
    
    target_ds.to_netcdf(target_file,mode='w')
    
    client.close()
    cluster.close()
