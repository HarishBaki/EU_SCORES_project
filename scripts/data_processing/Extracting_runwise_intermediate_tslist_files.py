import xarray as xr
import os
import glob
import dask.distributed as dd
import dask
import time
import sys
import calendar
from datetime import datetime, timedelta
import numpy as np
import wrf
import pandas as pd

def extract_variables_from_tslist(i,location,variable,dates):
    '''
    i: WRF run indice
    location: defines the tslist location
    variable: Either TS, UU, or VV, corresponding to the surface, UU wind, and VV wind. Other variables are not needed right now
    dates: wrf_run_dates dataframe
    '''
    tslist_file_path = glob.glob(f"../WRF_{i}/{location}.d01.{variable}")[0]
    print(tslist_file_path)
    if (variable=='TS'):
        df = pd.read_csv(tslist_file_path,delim_whitespace=True,skiprows=1,header=None,
                         low_memory=False,usecols=[1,5,7,8,50,51,52])
        df.columns = ['ts_hour','T2m','U10','V10','SWDOWN2','SWDDNI2','SWDDIF2']
        df = df.iloc[::2,:] # This is performed to the nan rows at every 2nd step, common thing
    else:
        df = pd.read_csv(tslist_file_path,delim_whitespace=True,skiprows=1,usecols=range(0,21),header=None,
                     low_memory=False)
    # get number of run days
    sim_days = (datetime(dates.loc[i][4],dates.loc[i][5],dates.loc[i][6],dates.loc[i][7]) - 
                datetime(dates.loc[i][0],dates.loc[i][1],dates.loc[i][2],dates.loc[i][3])).days
    steps_in_a_day = int(df.shape[0]/sim_days)
    timestep = int((24*60*60)/(steps_in_a_day)) # in seconds
    output_latency = 60 #in seconds, 3600 for 1 hr, 600 for 10min, 60 for 1min
    df = df.iloc[steps_in_a_day-1::int(output_latency/timestep),:] #from 24th hr to last output timestep

    times = pd.date_range(start=datetime(dates.loc[i][0],dates.loc[i][1],dates.loc[i][2],dates.loc[i][3]) + timedelta(days=1),
                  end=datetime(dates.loc[i][4],dates.loc[i][5],dates.loc[i][6],dates.loc[i][7]), periods=len(df))
    df.index = times
    # Discard the last time step, , since this one will be repeated in the next run, except in the 2265th run
    if (i != 2265):
        df = df.iloc[:-1]

    ## Before running the script, check the target file existence, and delete if true
    target_file_path = f'intermediate_files/{location}_{variable}_{i}.csv'
    if os.path.exists(target_file_path):
        os.remove(target_file_path)
    df.to_csv(target_file_path)
    print(f'Printing WRF run {i}')

if __name__ == "__main__":
    i = int(sys.argv[1])
    location = sys.argv[2]
    variable = sys.argv[3]
    #--Runs starting and ending dates, from the WRF_runs_dates file --#
    dates = pd.read_csv('../overall_WRF_run_dates_2.csv',index_col=0) 
    '''
    Should exist in the eval folder. Remember, dates has count as index, which starts from 1. 
    Since we want to access the runs, which also starts from 1, try using loc, instead of iloc, which will indeed use the python indexing, rathern than the keys.
    This will utterly change the time indexing, since we fullow the dates to appnd time index to the dataframes.
    '''
    extract_variables_from_tslist(i,location,variable,dates)
    
    
