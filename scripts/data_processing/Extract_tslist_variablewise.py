import xarray as xr
import os
import glob
import dask
import dask.array as da
import dask.dataframe as dd
from functools import partial
from dask.distributed import Client
from dask.diagnostics import ProgressBar
import time
import sys
import calendar
from datetime import datetime, timedelta
import numpy as np
import wrf

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
scripts_dir = f'{root_dir}/scripts'
sys.path.append(scripts_dir)

run = sys.argv[1]
case = sys.argv[2]
variable = sys.argv[3]
location = sys.argv[4]

import pandas as pd

if __name__ == "__main__":
    # Create a Dask cluster
    print("Starting parallel computing...")
    cluster = dask.distributed.LocalCluster(n_workers=24, dashboard_address=':22722')
    # Connect to the cluster
    client = dask.distributed.Client(cluster)
    print(client)

    run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed'
    target_file = f'{run_dir}/variablewise_files/{location}_{variable}.csv'

    start_time = time.time()
    df = dd.read_csv(f'{run_dir}/intermediate_files/{location}_{variable}*.csv').set_index('Unnamed: 0')
    dd.to_csv(df,target_file,single_file=True,compute=True)
    end_time = time.time()
    print(f'Elapsed time {end_time-start_time}s for {variable}')

    client.close()
    cluster.close()