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

import dask.distributed as dd
import dask
import dask.array as da

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import turbine_power

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

	run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
	os.system(f'mkdir -p {run_dir}/{turbine_type}')
	target_file = f'{run_dir}/{turbine_type}/tp_{level}.nc'

	print(run_dir,target_file)

	chunks={"Time": 240,"south_north": -1,"west_east": -1}
	ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']
	
	chunksize = 72000
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
