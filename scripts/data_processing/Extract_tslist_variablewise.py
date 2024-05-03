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

import pandas as pd

if __name__ == "__main__":
    # Create a Dask cluster
    print("Starting parallel computing...")
    cluster = dask.distributed.LocalCluster(n_workers=24, dashboard_address=':22722')
    # Connect to the cluster
    client = dask.distributed.Client(cluster)
    print(client)
    for variable in ['TS','UU','VV']:
        start_time = time.time()
        df = dd.read_csv(f'intermediate_files/POR2_{variable}*.csv').set_index('Unnamed: 0')
        dd.to_csv(df,f'variablewise_files/{variable}.csv',single_file=True,compute=True)
        end_time = time.time()
        print(f'Elapsed time {end_time-start_time}s for {variable}')
    client.close()
    cluster.close()