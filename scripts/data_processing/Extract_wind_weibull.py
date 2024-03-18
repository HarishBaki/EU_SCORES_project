import xarray as xr
import numpy as np
import sys
import time
from scipy.stats import weibull_min
import dask.distributed as dd

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import weibull

run = 'New_runs' #sys.argv[1]
case = 'Germany_coast' #sys.argv[2]
level = '10' #int(sys.argv[3])

run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'

start = time.time()
# Create a Dask cluster
print("Starting parallel computing...")
cluster = dd.LocalCluster(n_workers=12, dashboard_address=':22722')

# Connect to the cluster
client = dd.Client(cluster)
client

chunks={"Time": 240,"south_north": -1,"west_east": -1}
ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']

'''
create hourly, monthly, yearly, and overall parameters for the weibull distribution in the shape of 
2 parameters, time, lat, lon
'''
hourly_values = np.zeros((2,len(ws.Time.isel(Time=slice(None,-1)).groupby('Time.hour')),*ws.shape[1:]))
monthly_values = np.zeros((2,len(ws.Time.isel(Time=slice(None,-1)).groupby('Time.month')),*ws.shape[1:]))
yearly_values = np.zeros((2,len(ws.Time.isel(Time=slice(None,-1)).groupby('Time.year')),*ws.shape[1:]))
overall_values = np.zeros((2,*ws.shape[1:]))
print(hourly_values.shape, monthly_values.shape, yearly_values.shape, overall_values.shape)

def calculate_weibull(i,j,hourly_values,monthly_values,yearly_values,overall_values):
    for hour,data in enumerate(ws.isel(Time=slice(None,-1))[:,i,j].groupby('Time.hour')):
        start_time = time.time()
        shape, scale = weibull(data[1])
        hourly_values[:,hour,i,j] = shape, scale
        print(f'Cell {i},{j} at hour {hour} done in {time.time()-start_time} seconds, {shape},{scale}')
    
    for month,data in enumerate(ws.isel(Time=slice(None,-1))[:,i,j].groupby('Time.month')):
        start_time = time.time()
        shape, scale = weibull(data[1])
        monthly_values[:,month,i,j] = shape, scale
        print(f'Cell {i},{j} at month {month} done in {time.time()-start_time} seconds, {shape},{scale}')
    
    for year,data in enumerate(ws.isel(Time=slice(None,-1))[:,i,j].groupby('Time.year')):
        start_time = time.time()
        shape, scale = weibull(data[1])
        yearly_values[:,year,i,j] = shape, scale
        print(f'Cell {i},{j} at year {year} done in {time.time()-start_time} seconds, {shape},{scale}')
    
    start_time = time.time()
    shape, scale = weibull(ws.isel(Time=slice(None,-1))[:,i,j])
    overall_values[:,i,j] = shape, scale
    print(f'Cell {i},{j} done in {time.time()-start_time} seconds, {shape},{scale}')

from joblib import Parallel, delayed
arguments = [(i, j) for i in range(2) for j in range(2)]
Parallel(n_jobs=48,require='sharedmem',verbose=10)(
    delayed(calculate_weibull)(i, j,hourly_values,monthly_values,yearly_values,overall_values) for i, j in arguments)

# Create xarray dataset for hourly, monthly, yearly, and overall values
weibull_dataset = xr.Dataset({
    'hourly_values': (('parameter', 'hour', 'south_north', 'west_east'), hourly_values),
    'monthly_values': (('parameter', 'month', 'south_north', 'west_east'), monthly_values),
    'yearly_values': (('parameter', 'year', 'south_north', 'west_east'), yearly_values),
    'overall_values': (('parameter', 'south_north', 'west_east'), overall_values)
})

# Add coordinates
weibull_dataset['hour'] = range(24)
weibull_dataset['month'] = range(1, 13)
weibull_dataset['year'] = range(ws['Time.year'].min().values, ws['Time.year'].max().values)
weibull_dataset['parameter'] = ['shape', 'scale']