import xarray as xr
import pandas as pd
import numpy as np
from scipy.stats import weibull_min
import time
import glob

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project/CLLJ'

def wind_power_density(ws, rho=1.225):
    '''
    ws: xarray DataArray of wind speed, magnitude in m/s
    rho: float, air density in kg/m^3
    returns wpd: xarray DataArray of wind power density in W/m^2
    '''
    wpd = 0.5 * rho * ws**3
    wpd = xr.DataArray(wpd.astype('float32'),name='wpd')
    return wpd

def longitude_convert_0_to_360(lon):
    '''
    returns longitude in the range of 0 to 360
    '''
    return np.where(lon >= 0, lon, lon + 360)

def find_nearest_indice(ds_lat,ds_lon,target_lat=None, target_lon=None, lon_convert=None):
    '''
    ds_lat: xarray DataArray of latitude
    ds_lon: xarray DataArray of longitude
    target_lat: float, target latitude
    target_lon: float, target longitude
    lon_convert: bool, whether to convert the target longitude to the same range as the data
    returns indices: tuple of indices of the nearest grid point
    '''
    if lon_convert:
        # Convert the target longitude to the same range as the data
        target_lon = longitude_convert_0_to_360(target_lon)
    distance_squared = (ds_lat - target_lat)**2 + (ds_lon - target_lon)**2
    indices = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    print(f'Closest indices in the order of latitude (y) and longitude (x) are : {indices}')
    return indices

def regional_extraction(ds,target_grid, lon_convert=False):
    '''
    ds: xarray DataArray
    target_grid: dict, keys are 'min_lat','max_lat','min_lon','max_lon'
    returns data: xarray DataArray of the region
    Extracts CERRA subsets based on the target grid
    '''
    min_lon = longitude_convert_0_to_360(target_grid['min_lon']-1) if lon_convert else target_grid['min_lon']-1
    max_lon = longitude_convert_0_to_360(target_grid['max_lon']+1) if lon_convert else target_grid['max_lon']+1
    distance_squared = (ds.latitude - (target_grid['min_lat']-1))**2 + (ds.longitude - min_lon)**2
    indices_ll = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    distance_squared = (ds.latitude - (target_grid['max_lat']+1))**2 + (ds.longitude - max_lon)**2
    indices_uu = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    data = ds.sel(y=slice(indices_ll[0],indices_uu[0]),x = slice(indices_ll[1],indices_uu[1]))
    return data