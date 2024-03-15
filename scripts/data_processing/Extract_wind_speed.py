import xarray as xr
import dask.distributed as dd
import time
import sys
import numpy as np
import dask.distributed as dd
import os, sys

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import wind_speed

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
	
	run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
	target_name = f'ws_{level}'
	
	if level == 10:
		var1 = 'U10'
		var2 = 'V10'
		level = None
	else:
		var1 = 'U_ZL'
		var2 = 'V_ZL'
	print(run_dir,target_name,var1,var2)
	
	chunks={"Time": 3600,"south_north": -1,"west_east": -1}
	if level:
		ds1 = xr.open_dataset(f'{run_dir}/{var1}_{level}.nc',chunks=chunks)[var1]
		ds2 = xr.open_dataset(f'{run_dir}/{var2}_{level}.nc',chunks=chunks)[var2]
	else:
		ds1 = xr.open_dataset(f'{run_dir}/{var1}.nc',chunks=chunks)[var1]
		ds2 = xr.open_dataset(f'{run_dir}/{var2}.nc',chunks=chunks)[var2]
	
	ws = wind_speed(ds1,ds2)

	XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc')
	XLAT = XLAND.XLAT
	XLONG = XLAND.XLONG

	ws = ws.assign_coords(XLAT=XLAT,XLONG=XLONG).compute()
	
	client.close()
	cluster.close()
	
	ws.to_netcdf(f'{run_dir}/{target_name}.nc')
	end = time.time()
	print(f'Elapsed time for writing {target_name} is {end-start}s')
