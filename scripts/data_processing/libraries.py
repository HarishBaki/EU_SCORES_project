import xarray as xr
import pandas as pd
import numpy as np
from scipy.stats import weibull_min

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'

def wind_speed(ds1,ds2): 
    ws = xr.DataArray(np.sqrt(ds1**2 + ds2**2), name='ws')
    return ws 

def turbine_power(wind,turbine_type=None):
    # Fix the spline approximation
    from scipy.interpolate import UnivariateSpline
    if turbine_type == '15MW':
        power_curve = pd.read_csv(f'{root_dir}/IEA_15MW_240_RWT.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=3) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error
    elif turbine_type == '8MW':
        power_curve = pd.read_csv(f'{root_dir}/LEANWIND_8MW_164_RWT.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=4) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error

    #Convert the power array to float32 and change it to xarray DataArray
    power = xr.DataArray(power.astype('float32'),name='power')
    return power

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

def weibull(data):
    data = data
    data = np.where(data == 0, np.nan, data)
    data = data[~np.isnan(data)]
    data = np.sort(data)
    shape, _, scale = weibull_min.fit(data, floc=0)
    return shape, scale