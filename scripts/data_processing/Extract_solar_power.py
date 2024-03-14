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

def solar_power(ws,swdown,t2,Epv):
    # Based on Rui Chang et. al., 2022, A coupled WRF-PV mesoscale model simulating the near-surface climate of utility-scale photovoltaic plants
    # Based on https://www.sciencedirect.com/science/article/pii/S0959652623011551#sec2
    c1 = 4.3 # degC
    c2 = 0.943 # No units
    c3 = 0.028 # degC.m2.W-1
    c4 = -1.528 # degC.s.m-1
    gamma = - 0.005 # degC-1   
    
    Tcell = c1 + c2*t2 + c3*swdown + c4*ws
    Tref = 25

    PR = 1 + gamma * (Tcell - Tref) 
    Spv = swdown * Epv * PR
    Spv = xr.DataArray(Spv.astype('float32'),name='PVO')
    return Spv

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

	root_dir = '/media/harish/SSD_4TB/EU_SCORES'
	run_dir=f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files'
	target_file = f'{run_dir}/spv.nc'

	print(run_dir,target_file)

	chunks={"Time": 240,"south_north": -1,"west_east": -1}
	
	XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc')
	XLAT = XLAND.XLAT
	XLONG = XLAND.XLONG

	ws = xr.open_dataset(f'{run_dir}/ws_10.nc',chunks=chunks)['ws']
	t2m = xr.open_dataset(f'{run_dir}/T2.nc',chunks=chunks)
	t2m = t2m['T2'].assign_coords(XLAT=XLAT,XLONG=XLONG)-273.16
	swdown = xr.open_dataset(f'{run_dir}/SWDOWN2.nc',chunks=chunks)
	swdown = swdown['SWDOWN2'].assign_coords(XLAT=XLAT,XLONG=XLONG)
	
	chunksize = 7200
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
