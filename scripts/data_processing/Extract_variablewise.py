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
    

    
    folders = [f for f in os.listdir('variablewise_files') if os.path.isdir(os.path.join('variablewise_files', f)) and not f.startswith('.')]
    # Define a custom sorting function to sort folders based on the numerical part
    def custom_sort(folder_name):
        return int(folder_name.split('-')[0])
    # Sort the list of folders using the custom sorting function
    folders = sorted(folders, key=custom_sort)

    vars = ['U10','V10','T2','SWDOWN2']
    vars = ['T2']
    for var in vars:
        # Create a Dask cluster
        print("Starting parallel computing...")
        cluster = dd.LocalCluster(n_workers=48, dashboard_address=':22722')

        # Connect to the cluster
        client = dd.Client(cluster)
        print(client)
            
        start_time = time.time()
        print(f'Working on {var}')
        target_file = f'variablewise_files/{var}.nc'
        if os.path.exists(target_file):
            os.remove(target_file)

        file_names = []
        for folder in folders:
            file_path = os.path.join(f'variablewise_files/{folder}', f'{var}.nc')

            # Check if 'var.nc' exists in the folder
            if os.path.exists(file_path):
                file_names.append(file_path)
        print(file_names)
        
        chunks={"Time": 24*100,"south_north": -1,"west_east": -1}
        combined_ds = xr.open_mfdataset(file_names,chunks=chunks,
                               combine='nested',
                               concat_dim='Time',
                               parallel=True)
        
        ds = combined_ds[var]
        ds.to_netcdf(f'{target_file}')
        
        end_time = time.time()
        print(f'Elapsed time {end_time-start_time}s for {var}')
        ds.close()
        
        client.close()
        cluster.close()
    '''
    vars = ['U_ZL','V_ZL']
    levels = [80,100,120,150]
    for var in vars:
        for level in levels:
            # Create a Dask cluster
            print("Starting parallel computing...")
            cluster = dd.LocalCluster(n_workers=48, dashboard_address=':22722')

            # Connect to the cluster
            client = dd.Client(cluster)
            print(client)

            print(f'Working on {var} at {level}')
            start_time = time.time()
            target_file = f'variablewise_files/{var}_{level}.nc'
            if os.path.exists(target_file):
                os.remove(target_file)

            file_names = []
            for folder in folders:
                file_path = os.path.join(f'variablewise_files/{folder}', f'{var}_{level}.nc')

                # Check if 'var.nc' exists in the folder
                if os.path.exists(file_path):
                    file_names.append(file_path)
            print(file_names)

            chunks={"Time": 24*100,"south_north": -1,"west_east": -1}
            combined_ds = xr.open_mfdataset(file_names,chunks=chunks,
                                             combine='nested',
                                             concat_dim='Time',
                                             parallel=True)
            ds = combined_ds[var]
            ds.to_netcdf(f'{target_file}')

            end_time = time.time()
            print(f'Elapsed time {end_time-start_time}s for {var} at {level}')
            ds.close()

            client.close()
            cluster.close()
    '''
