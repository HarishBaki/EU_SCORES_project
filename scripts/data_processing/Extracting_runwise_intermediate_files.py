import xarray as xr
import os
import glob
import dask.distributed as dd
import dask
import time
import sys
import calendar
from datetime import datetime
import numpy as np
import wrf
import pandas as pd

def subset_file(i):
    wrf_file = glob.glob(f"../WRF_{i}/wrfout_d01*")[0]
    aux_file = glob.glob(f"../WRF_{i}/auxhist22_d01*")[0]
    ds_wrf = xr.open_dataset(wrf_file)
    ds_aux = xr.open_dataset(aux_file)

    # Create a new dataset with the 3D variables from aux and surface variables from wrfout
    ds = ds_aux[['Times','U10','V10','T2','U_ZL','V_ZL']] #Exclude TImes, since it is causing trouble due to missing values
    ds["SWDOWN2"] = ds_wrf['SWDOWN2']
    ds["XLAT"] = ds_aux.XLAT.isel(Time=0)
    ds["XLONG"] = ds_aux.XLAT.isel(Time=0)
	
    '''
    # --- appending the Times ---#
    # Get the row for the specified index
    row = df.iloc[i]
    # Generate the time range for the specified count
    start_datetime = pd.to_datetime(f'{row["start_year"]}-{row["start_month"]}-{row["start_day"]} {row["start_hour"]:02}', format='%Y-%m-%d %H')
    end_datetime = pd.to_datetime(f'{row["end_year"]}-{row["end_month"]}-{row["end_day"]} {row["end_hour"]:02}', format='%Y-%m-%d %H')
    datetime_range = pd.date_range(start=start_datetime, end=end_datetime, freq='H')
    
    # Create a new DataArray for 'Times'
    times_dataarray = xr.DataArray(datetime_range, dims=ds_aux['Time'].dims)
    
    # Assign the new 'Times' DataArray to the dataset
    ds['Times'] = times_dataarray.drop_vars('Time')
    '''
    # Discard the first day of simulation
    if (i != 2265):
        ds = ds.isel(Time=slice(24, -1))
    else:
        ds = ds.isel(Time=slice(24, None))
    
    # Assign the num_z_level_stag coordinates 
    ds = ds.assign_coords(num_z_levels_stag=ds_aux.Z_ZL[0].values).sel(num_z_levels_stag=slice(80,150))

    ## Before running the script, check the target file existence, and delete if true
    target_file = f'intermediate_files/WRF_{i}.nc'

    if os.path.exists(target_file):
        os.remove(target_file)
        print(f"File '{target_file}' deleted.")
    
    ds.to_netcdf(target_file)
    print(f'Done writing WRF_{i}')

if __name__ == "__main__":
    #df = pd.read_csv('../overall_WRF_run_dates_2.csv',index_col=0)
    '''
    # Create a Dask cluster
    print("Starting parallel computing...")
    cluster = dd.LocalCluster(n_workers=8, dashboard_address=':22622')

    # Connect to the cluster
    client = dd.Client(cluster)
    print(client)
    
    #The following is the method for submitting jobs in parallel and distributed
    print("Extracting intermediate subset data...")
    results = []
    start = time.time()
    for i in range(1303,1313+1):
        f = client.submit(subset_file, i)
        results.append(f)
    client.gather(results)
    end = time.time()
    print(f"{end - start} s elapsed in Subsetting")
    
    client.close()
    cluster.close()
    '''
    i = int(sys.argv[1])
    subset_file(i)
    
