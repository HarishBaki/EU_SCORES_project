import xarray as xr
import numpy as np
import sys, os, glob
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import regional_extraction

if __name__ == '__main__':
    # load inputs from bash
    var_dir = sys.argv[1]
    variable = sys.argv[2]

    '''
    # Create a Dask cluster
    print("Starting parallel computing...")
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=24,threads_per_worker=1,processes=True,dashboard_address=':8787')
    # Connect to the cluster
    client = dd.Client(cluster)
    ''' 

    # Load the CERRA data
    run_dir = f'{root_dir}/CERRA'
    files = sorted(glob.glob(f'{run_dir}/{var_dir}/CERRA_*.nc'))
    chunks={"time": 96,"x": -1,"y": -1}
    ds = xr.open_mfdataset(files,chunks=chunks,concat_dim='time',combine='nested',parallel=True)
    data = ds.sel(time=slice('1990-01-01T00','2021-01-01T00'))

    # target grids
    target_grids = {'Portugal': {'min_lat': 41.25, 'min_lon': -9.35,'max_lat':41.8,'max_lon':-8.65},
            'Ireland': {'min_lat': 52.49, 'min_lon': -10.51,'max_lat':53,'max_lon':-9.7},
            'BeNeLux': {'min_lat': 50.95, 'min_lon': 2.25,'max_lat':51.8,'max_lon':3.55}}
    
    for region in target_grids:
        # mkdir run_dir/region
        if not os.path.exists(f'{run_dir}/{region}'):
            os.makedirs(f'{run_dir}/{region}')
            os.makedirs(f'{run_dir}/{region}/variablewise_files')
        
        target_grid = target_grids[region]
        data_region = regional_extraction(data,target_grid)
        data_region = xr.DataArray(data_region.to_array().astype('float32'),name=variable)
        # target file 
        target_file = f'{run_dir}/{region}/variablewise_files/{var_dir}.nc'
        if os.path.exists(target_file):
            os.remove(target_file)
        data_region.to_netcdf(target_file)
        print(f'{variable} for {region} is extracted and saved')

    # Close the cluster
    #client.close()
    #cluster.close()


