import xarray as xr
import pandas as pd
import numpy as np
import time
import glob, sys, os

root_dir = '/media/ssd_4tb_qvo/EU_SCORES_project/WRFV4.4/FLLJ/'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

from data_processing.libraries import *

case = int(sys.argv[1])
case_dir = f'FLLJ_{case}'
run = int(sys.argv[2])
run_dir = sys.argv[3]
event_periods = [['2016-02-21T18:00','2016-02-22T18:00'],['2016-03-03T18:00','2016-03-04T18:00'],
                 ['2016-02-09-T00:00','2016-02-10-T00:00'],['2017-01-09-T12:00','2017-01-10-T12:00'],
                 ['2017-01-29-T12:00','2017-01-30-T12:00']] # don't put seconds in the time string
if __name__ == '__main__':
    # Connect to the dask cluster
    import dask.distributed as dd
    cluster = dd.LocalCluster(n_workers=24, threads_per_worker=2, memory_limit='2GB',dashboard_address='22522')
    client = dd.Client(cluster)
    print(client)
    
    dates_range = event_periods[case-1]
    if run == 1 or run == 2 or run == 5 or run == 8 or run == 9 or run == 12 or run == 16 or run == 17:
        overall_power = extract_POWER(root_dir, case_dir,run,run_dir,dates_range)
        # Save the data
        # remove file if exist
        try:
            os.remove(f'{root_dir}/{case_dir}/{run_dir}/turbine_power.nc')
        except:
            pass
        overall_power.to_netcdf(f'{root_dir}/{case_dir}/{run_dir}/turbine_power.nc')

    client.close()
    cluster.close()