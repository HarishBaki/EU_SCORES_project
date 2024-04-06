import xarray as xr
import numpy as np
import sys
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

def overall_statistic(ds,statistic,time_coord='Time',quantile=None):
    if statistic == 'std':
        return ds.std(dim=time_coord).compute()
    elif statistic == 'quantile':
        return ds.quantile(quantile,dim=time_coord,method='inverted_cdf').compute()
    else:
        print(f'Invalid statistic {statistic}')
        return None

if __name__ == '__main__':
    run = sys.argv[1]
    case = sys.argv[2]
    file_name = sys.argv[3]
    variable = sys.argv[4]
    n_workers = int(sys.argv[5])
    dashboard_port = sys.argv[6]

	# Create a Dask cluster
    print("Starting parallel computing...")
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=n_workers,threads_per_worker=2,memory_limit='2GB',dashboard_address=f':{dashboard_port}')
    # Connect to the cluster
    client = dd.Client(cluster)
    print(client)

    chunks={"Time": -1,"south_north": 8,"west_east": 8}

    run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
    target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/statistics_files/{file_name}'

    source_ds = xr.open_dataset(f'{run_dir}/{file_name}.nc',chunks=chunks)[variable]
    data = source_ds.isel(Time=slice(None,-1))

    XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc').load()
    XLAT = XLAND.XLAT
    XLONG = XLAND.XLONG

    # === std ===#
    start = time.time()
    print('Calculating std statistics')
    statistic = 'std'
    with xr.open_dataset(f'{target_dir}/{statistic}.nc') as target_ds:
        target_ds['overall_values'] = overall_statistic(data,statistic)
        target_ds = target_ds.load()
        # chech if XLAT and XLONG are present in the dataset, if not, add them to data
        if 'XLAT' not in target_ds.coords or 'XLONG' not in target_ds.coords:
            target_ds = target_ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    # save the ds to the same file
    target_ds.to_netcdf(f'{target_dir}/{statistic}.nc',mode='w')
    print(f'Time taken for std calculation: {time.time()-start}')

    # === CoV ===#
    start = time.time()
    print('Calculating CoV statistics')
    statistic = 'cov'
    std = xr.open_dataset(f'{target_dir}/std.nc')
    mean = xr.open_dataset(f'{target_dir}/mean.nc')
    cov = (std/mean)
    with xr.open_dataset(f'{target_dir}/{statistic}.nc') as target_ds:
        target_ds['overall_values'] = cov['overall_values']
        target_ds = target_ds.load()
        # chech if XLAT and XLONG are present in the dataset, if not, add them to data
        if 'XLAT' not in target_ds.coords or 'XLONG' not in target_ds.coords:
            target_ds = target_ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    # save the ds to the same file
    target_ds.to_netcdf(f'{target_dir}/{statistic}.nc',mode='w')
    print(f'Time taken for CoV calculation: {time.time()-start}')

    '''
    # === 5th quantile ===#
    start = time.time()
    print('Calculating 5th quantile statistics')
    statistic = 'quantile'
    quantile = 0.05
    with xr.open_dataset(f'{target_dir}/{statistic}_5.nc') as target_ds:
        target_ds['overall_values'] = overall_statistic(data,statistic,time_coord='Time',quantile=quantile)
        target_ds = target_ds.load()
        # chech if XLAT and XLONG are present in the dataset, if not, add them to data
        if 'XLAT' not in target_ds.coords or 'XLONG' not in target_ds.coords:
            target_ds = target_ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    # save the ds to the same file
    target_ds.to_netcdf(f'{target_dir}/{statistic}_5.nc',mode='w')
    print(f'Time taken for 5th quantile calculation: {time.time()-start}')

    # === 95th quantile ===#
    start = time.time()
    print('Calculating 95th quantile statistics')
    statistic = 'quantile'
    quantile = 0.95
    with xr.open_dataset(f'{target_dir}/{statistic}_95.nc') as target_ds:
        target_ds['overall_values'] = overall_statistic(data,statistic,time_coord='Time',quantile=quantile)
        target_ds = target_ds.load()
        # chech if XLAT and XLONG are present in the dataset, if not, add them to data
        if 'XLAT' not in target_ds.coords or 'XLONG' not in target_ds.coords:
            target_ds = target_ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    # save the ds to the same file
    target_ds.to_netcdf(f'{target_dir}/{statistic}_95.nc',mode='w')
    print(f'Time taken for 95th quantile calculation: {time.time()-start}')

    # === 99th quantile ===#
    start = time.time()
    print('Calculating 99th quantile statistics')
    statistic = 'quantile'
    quantile = 0.99
    with xr.open_dataset(f'{target_dir}/{statistic}_99.nc') as target_ds:
        target_ds['overall_values'] = overall_statistic(data,statistic,time_coord='Time',quantile=quantile)
        target_ds = target_ds.load()
        # chech if XLAT and XLONG are present in the dataset, if not, add them to data
        if 'XLAT' not in target_ds.coords or 'XLONG' not in target_ds.coords:
            target_ds = target_ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    # save the ds to the same file
    target_ds.to_netcdf(f'{target_dir}/{statistic}_99.nc',mode='w')
    print(f'Time taken for 99th quantile calculation: {time.time()-start}')
    '''

    client.close()
    cluster.close()