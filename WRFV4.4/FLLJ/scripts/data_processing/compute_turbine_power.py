import xarray as xr
import pandas as pd
import numpy as np
import time
import glob, sys, os

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project/WRFV4.4/FLLJ/'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import *

case = int(sys.argv[1])
case_dir = f'FLLJ_{case}'
run = int(sys.argv[2])
run_dir = sys.argv[3]
j = int(sys.argv[4])
combine = sys.argv[5]

event_periods = [['2016-02-21T18:00','2016-02-22T18:00'],['2016-03-03T18:00','2016-03-04T18:00'],
                 ['2016-02-09-T00:00','2016-02-10-T00:00'],['2017-01-09-T12:00','2017-01-10-T12:00'],
                 ['2017-01-29-T12:00','2017-01-30-T12:00']] # don't put seconds in the time string

if __name__ == '__main__':
    if combine == 'False':
        dates_range = event_periods[case-1]
        location = [turbine_lats[j],turbine_lons[j]]
        power_curve = power_curves[turbine_types[j]-1]
        levels = hub_heights[turbine_types[j]-1]
        u,v,XLONG,XLAT = extract_u_v(root_dir,case_dir,run,run_dir,dates_range,levels,location)
        ws = wind_speed(u,v)
        power_output = turbine_power(ws,power_curve.values)

        # make the directory if not exist
        target_dir = f'{root_dir}/{case_dir}/{run_dir}/.cache'
        if not os.path.exists(f'{target_dir}'):
            os.makedirs(f'{target_dir}')

        # remove if file exist
        target_file = f'{target_dir}/{j}.nc'
        if os.path.exists(target_file):
            os.remove(target_file)
        power_output.to_netcdf(target_file)
    else:
        files = glob.glob(f'{root_dir}/{case_dir}/{run_dir}/.cache/*.nc')
        ds = xr.open_mfdataset(files, combine='nested',concat_dim='turbine', parallel=True)
        power_output = ds.power.sum(dim='turbine')
        
        # remove if file exist
        target_file = f'{root_dir}/{case_dir}/{run_dir}/turbine_power.nc'
        if os.path.exists(target_file):
            os.remove(target_file)
        power_output.to_netcdf(target_file)
    

