import xarray as xr
import pandas as pd
import os
import glob
import dask.distributed as dd
import dask
import dask.array as da
import time
import sys
import calendar
from datetime import datetime, timedelta
import numpy as np
import wrf
from itertools import product

from dask.diagnostics import ProgressBar

import dask.distributed as dd
import dask
import dask.array as da

def turbine_power(wind,turbine_type=None):
    # Fix the spline approximation
    from scipy.interpolate import UnivariateSpline
    if turbine_type == '15MW':
        power_curve = pd.read_csv(f'{root_dir}/eval/IEA_15MW_240_RWT.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=3) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error
    elif turbine_type == '8MW':
        power_curve = pd.read_csv(f'{root_dir}/eval/LEANWIND_8MW_164_RWT.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=4) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error

    #Convert the power array to float32 and change it to xarray DataArray
    power = xr.DataArray(power.astype('float32'),name='power')
    return power

if __name__ == "__main__":
	
	start = time.time()
	# Create a Dask cluster
	print("Starting parallel computing...")
	cluster = dd.LocalCluster(n_workers=12, dashboard_address=':22722')

	# Connect to the cluster
	client = dd.Client(cluster)

	run = sys.argv[1]
	case = sys.argv[2]
	level = int(sys.argv[3])
	turbine_type = str(sys.argv[4])

	root_dir = '/media/harish/SSD_4TB/EU_SCORES'
	run_dir=f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files'
	os.system(f'mkdir -p {run_dir}/{turbine_type}')
	target_file = f'{run_dir}/{turbine_type}/tp_{level}.nc'

	print(run_dir,target_file)

	chunks={"Time": 240,"south_north": -1,"west_east": -1}
	ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']
	
	chunksize = 7200
	# first chunk computation 
	i = 0
	start = time.time()
	chunk = ws.isel(Time=slice(i, i + chunksize)).compute()
	end = time.time()
	print(f'{i} to {i+chunksize} ws loading takes {end - start}s')

	start = time.time()
	power_chunk = turbine_power(chunk, turbine_type=turbine_type)
	end = time.time()
	print(f'{i} to {i+chunksize} chunk power computation takes {end - start}s')
	
	tp = power_chunk
	del chunk, power_chunk
	
	for i in range(chunksize, ws.Time.size, chunksize):
		start = time.time()
		chunk = ws.isel(Time=slice(i, i + chunksize)).compute()
		end = time.time()
		print(f'{i} to {i+chunksize} ws loading takes {end - start}s')

		start = time.time()
		power_chunk = turbine_power(chunk, turbine_type=turbine_type)
		end = time.time()
		print(f'{i} to {i+chunksize} power computation takes {end - start}s')

		start = time.time()
		tp = xr.concat([tp, power_chunk], dim='Time')
		end = time.time()
		print(f'{i} to {i+chunksize} concatenate takes {end - start}s')
		
		del chunk, power_chunk
		
	client.close()
	cluster.close()

	if os.path.exists(target_file):
		os.remove(target_file)

	start = time.time()
	tp.to_netcdf(target_file)
	end = time.time()
	print(f'Wtiting {target_file} takes {end-start}s')
