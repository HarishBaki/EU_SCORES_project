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
from itertools import product

from dask.diagnostics import ProgressBar

import dask.distributed as dd
import dask
import dask.array as da

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import solar_power

if __name__ == "__main__":
	
	start = time.time()
	# Create a Dask cluster
	print("Starting parallel computing...")
	cluster = dd.LocalCluster(n_workers=48, dashboard_address=':22722')

	# Connect to the cluster
	client = dd.Client(cluster)

	run = sys.argv[1]
	case = sys.argv[2]
	Epv = 0.216

	run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
	target_file = f'{run_dir}/spv.nc'

	print(run_dir,target_file)

	chunks={"Time": 240,"south_north": -1,"west_east": -1}
	
	XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc')
	XLAT = XLAND.XLAT
	XLONG = XLAND.XLONG

	ws = xr.open_dataset(f'{run_dir}/ws_10.nc',chunks=chunks)['ws']
	t2m = xr.open_dataset(f'{run_dir}/T2.nc',chunks=chunks)
	t2m = t2m['T2'].assign_coords(XLAT=XLAT,XLONG=XLONG)
	swdown = xr.open_dataset(f'{run_dir}/SWDOWN2.nc',chunks=chunks)
	swdown = swdown['SWDOWN2'].assign_coords(XLAT=XLAT,XLONG=XLONG)
	
	chunksize = 72000
	# first chunk computation 
	i = 0
	start = time.time()
	wschunk = ws.isel(Time=slice(i, i + chunksize)).compute()
	t2mchunk = t2m.isel(Time=slice(i, i + chunksize)).compute()
	swdownchunk = swdown.isel(Time=slice(i, i + chunksize)).compute()
	end = time.time()
	print(f'{i} to {i+chunksize} loading takes {end - start}s')

	start = time.time()
	spv_chunk = solar_power(wschunk, swdownchunk,t2mchunk, Epv)
	end = time.time()
	print(f'{i} to {i+chunksize} chunk power computation takes {end - start}s')
	
	spv = spv_chunk
	del wschunk,t2mchunk,swdownchunk, spv_chunk
	
	for i in range(chunksize, swdown.Time.size, chunksize):
		start = time.time()
		wschunk = ws.isel(Time=slice(i, i + chunksize)).compute()
		t2mchunk = t2m.isel(Time=slice(i, i + chunksize)).compute()
		swdownchunk = swdown.isel(Time=slice(i, i + chunksize)).compute()
		end = time.time()
		print(f'{i} to {i+chunksize} loading takes {end - start}s')

		start = time.time()
		spv_chunk = solar_power(wschunk, swdownchunk,t2mchunk, Epv)
		end = time.time()
		print(f'{i} to {i+chunksize} power computation takes {end - start}s')

		start = time.time()
		spv = xr.concat([spv, spv_chunk], dim='Time')
		end = time.time()
		print(f'{i} to {i+chunksize} concatenate takes {end - start}s')
		
		del wschunk,t2mchunk,swdownchunk, spv_chunk
		
	client.close()
	cluster.close()

	if os.path.exists(target_file):
		os.remove(target_file)

	start = time.time()
	spv.to_netcdf(target_file)
	end = time.time()
	print(f'Wtiting {target_file} takes {end-start}s')
