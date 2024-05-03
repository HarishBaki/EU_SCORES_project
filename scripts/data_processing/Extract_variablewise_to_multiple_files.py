import xarray as xr
import os
import glob
import dask.distributed as dd
import dask
import dask.array as da
from functools import partial
from dask.distributed import Client
from dask.diagnostics import ProgressBar
import time
import sys
import calendar
from datetime import datetime, timedelta
import numpy as np
import wrf

import pandas as pd

if __name__ == "__main__":
    
    # Create a Dask cluster
    print("Starting parallel computing...")
    cluster = dd.LocalCluster(n_workers=48, dashboard_address=':22722')

    # Connect to the cluster
    client = dd.Client(cluster)
    print(client)
    
    run_start = 1211
    run_delta = 404
    run_final = 1614
    while run_start <= run_final:
        run_end = run_start + run_delta
        run_end = run_end if run_end<run_final else run_final

        file_paths = [glob.glob(f'intermediate_files/WRF_{i}.nc')[0] for i in range(run_start,run_end+1)]

        combined_ds = xr.open_mfdataset(file_paths,
                           combine='nested',
                           concat_dim='Time',
                           parallel=True)

        OUTPUT_DIR = f'variablewise_files/{run_start}-{run_end}'
        os.system(f'mkdir -p {OUTPUT_DIR}')

        #hourly_range = pd.date_range(start=pd.to_datetime('1990-01-01 00:00'), end=pd.to_datetime('2020-01-01 00:00'), freq='H')
        #hourly_range = pd.date_range(start=pd.to_datetime(np.char.decode(combined_ds.Times.values[0], 'utf-8'), format='%Y-%m-%d_%H:%M:%S'),
        #                         end=pd.to_datetime(np.char.decode(combined_ds.Times.values[-1], 'utf-8'), format='%Y-%m-%d_%H:%M:%S'), freq='H')
        hourly_range = pd.to_datetime(np.char.decode(combined_ds.Times, 'utf-8'), format='%Y-%m-%d_%H:%M:%S')

        vars = ['U10','V10','T2','SWDOWN2']
        for var in vars:
            start_time = time.time()
            print(f'Working on {var}')
            target_file = f'{OUTPUT_DIR}/{var}.nc'
            if os.path.exists(target_file):
                os.remove(target_file)
            ds = combined_ds[var].chunk(Time=-1,south_north=16,west_east=16).assign_coords(Time=hourly_range)
            ds = ds.where(ds != 9.96921e+36, np.nan)
            ds.to_netcdf(f'{target_file}')
            end_time = time.time()
            print(f'Elapsed time {end_time-start_time}s for {var}')

        vars = ['U_ZL','V_ZL']
        levels = [80,100,120,150]
        for var in vars:
            for level in levels:
                print(f'Working on {var} at {level}')
                start_time = time.time()
                target_file = f'{OUTPUT_DIR}/{var}_{level}.nc'
                if os.path.exists(target_file):
                    os.remove(target_file)
                ds = combined_ds[var].sel(num_z_levels_stag=level).chunk(Time=-1,south_north=16,west_east=16
                                                                   ).assign_coords(Time=hourly_range)
                ds = ds.where(ds != 9.96921e+36, np.nan)
                ds.to_netcdf(f'{target_file}')
                end_time = time.time()
                print(f'Elapsed time {end_time-start_time}s for {var} at {level}')
        
        run_start = run_end+1
          
    client.close()
    cluster.close()
