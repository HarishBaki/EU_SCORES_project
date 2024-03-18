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

run = sys.argv[1]
case = sys.argv[2]
level = int(sys.argv[3])
i = int(sys.argv[4])
j = int(sys.argv[5])

run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files/weibull_{level}'

chunks={"Time": -1,"south_north": 1,"west_east": 1}
ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']

def calculate_weibull(i,j):
    start = time.time()
    data = ws.isel(Time=slice(None,-1))[:,i,j].load()
    hourly_values = np.zeros((2,len(data.groupby('Time.hour'))))
    for hour,hourly_data in enumerate(data.groupby('Time.hour')):
        shape, scale = weibull(hourly_data[1])
        hourly_values[:,hour] = shape, scale
    monthly_values = np.zeros((2,len(data.groupby('Time.month'))))
    for month,monthly_data in enumerate(data.groupby('Time.month')):
        shape, scale = weibull(monthly_data[1])
        monthly_values[:,month] = shape, scale
    yearly_values = np.zeros((2,len(data.groupby('Time.year'))))
    for year,yearly_data in enumerate(data.groupby('Time.year')):
        shape, scale = weibull(yearly_data[1])
        yearly_values[:,year] = shape, scale
    overall_values = np.zeros((2))
    shape, scale = weibull(data)
    overall_values[:] = shape, scale
    
    # Create xarray dataset for hourly, monthly, yearly, and overall values
    weibull_dataset = xr.Dataset({
        'hourly_values': (('parameter', 'hour'), hourly_values),
        'monthly_values': (('parameter', 'month'), monthly_values),
        'yearly_values': (('parameter', 'year'), yearly_values),
        'overall_values': (('parameter'), overall_values)
    })

    # Add coordinates
    weibull_dataset['hour'] = range(24)
    weibull_dataset['month'] = range(1, 13)
    weibull_dataset['year'] = range(ws['Time.year'].min().values, ws['Time.year'].max().values)
    weibull_dataset['parameter'] = ['shape', 'scale']
    weibull_dataset['south_north'] = i
    weibull_dataset['west_east'] = j

    weibull_dataset.to_netcdf(f'{target_dir}/{i}_{j}.nc')
    
    #print(f'{i}_{j} done in {time.time()-start} seconds')

if __name__ == '__main__':
    calculate_weibull(i,j)
