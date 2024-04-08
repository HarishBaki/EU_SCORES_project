import xarray as xr
import pandas as pd
import numpy as np
from scipy.stats import weibull_min
import time

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'

def wind_speed(ds1,ds2):
    '''
    ds1: xarray DataArray of u-component of wind
    ds2: xarray DataArray of v-component of wind
    returns ws: xarray DataArray of wind speed, magnitude in m/s
    ''' 
    ws = xr.DataArray(np.sqrt(ds1**2 + ds2**2), name='ws')
    return ws 

def wind_power_density(ws, rho=1.225):
    '''
    ws: xarray DataArray of wind speed, magnitude in m/s
    rho: float, air density in kg/m^3
    returns wpd: xarray DataArray of wind power density in W/m^2
    '''
    wpd = 0.5 * rho * ws**3
    wpd = xr.DataArray(wpd.astype('float32'),name='wpd')
    return wpd

def turbine_power(wind,turbine_type=None):
    '''
    wind: xarray DataArray of wind speed
    turbine_type: str, type of turbine, either '15MW' or '8MW'
    returns power: xarray DataArray of power, in KW
    '''
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
    '''
    ws: xarray DataArray of wind speed, magnitude in m/s
    swdown: xarray DataArray of downward shortwave radiation in W/m^2
    t2: xarray DataArray of temperature at 2m in degC
    Epv: float, efficiency of PV panel
    returns Spv: xarray DataArray of solar power in W/m^2
    '''
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

def regional_extraction(ds,target_grid):
    '''
    ds: xarray DataArray
    target_grid: dict, keys are 'min_lat','max_lat','min_lon','max_lon'
    returns data: xarray DataArray of the region
    Extracts CERRA subsets based on the target grid
    '''
    min_lon = longitude_convert_0_to_360(target_grid['min_lon']-1)
    max_lon = longitude_convert_0_to_360(target_grid['max_lon']+1)
    distance_squared = (ds.latitude - (target_grid['min_lat']-1))**2 + (ds.longitude - min_lon)**2
    indices_ll = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    distance_squared = (ds.latitude - (target_grid['max_lat']+1))**2 + (ds.longitude - max_lon)**2
    indices_uu = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    data = ds.sel(y=slice(indices_ll[0],indices_uu[0]),x = slice(indices_ll[1],indices_uu[1]))
    return data

def weibull(data):
    data = data
    data = np.where(data == 0, np.nan, data)
    data = data[~np.isnan(data)]
    data = np.sort(data)
    shape, _, scale = weibull_min.fit(data, floc=0)
    return shape, scale

def mean_statistics(data,time_coord='Time'):
    statistics = xr.Dataset()
    start = time.time()
    statistics['hourly_values'] = data.groupby(f'{time_coord}.hour').mean(dim=time_coord).compute()
    print(f'Hourly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['monthly_values'] = data.groupby(f'{time_coord}.month').mean(dim=time_coord).compute()
    print(f'Monthly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['yearly_values'] = data.groupby(f'{time_coord}.year').mean(dim=time_coord).compute()
    print(f'Yearly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['overall_values'] = data.mean(dim=time_coord).compute()
    print(f'Overall statistics calculated in {time.time()-start} seconds')

    return statistics

def std_statistics(data,time_coord='Time'):
    statistics = xr.Dataset()
    start = time.time()
    statistics['hourly_values'] = data.groupby(f'{time_coord}.hour').std(dim=time_coord).compute()
    print(f'Hourly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['monthly_values'] = data.groupby(f'{time_coord}.month').std(dim=time_coord).compute()
    print(f'Monthly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['yearly_values'] = data.groupby(f'{time_coord}.year').std(dim=time_coord).compute()
    print(f'Yearly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['overall_values'] = data.std(dim=time_coord).compute()
    print(f'Overall statistics calculated in {time.time()-start} seconds')

    return statistics

def quantile_statistics(data,quantile,time_coord='Time'):
    statistics = xr.Dataset()
    start = time.time()
    statistics['hourly_values'] = data.groupby(f'{time_coord}.hour').quantile(quantile,dim=time_coord,method='inverted_cdf').compute()
    print(f'Hourly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['monthly_values'] = data.groupby(f'{time_coord}.month').quantile(quantile,dim=time_coord,method='inverted_cdf').compute()
    print(f'Monthly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['yearly_values'] = data.groupby(f'{time_coord}.year').quantile(quantile,dim=time_coord,method='inverted_cdf').compute()
    print(f'Yearly statistics calculated in {time.time()-start} seconds')
    start = time.time()
    statistics['overall_values'] = data.quantile(quantile,dim=time_coord,method='inverted_cdf').compute()
    print(f'Overall statistics calculated in {time.time()-start} seconds')

    return statistics


def weibull_statistics(ws, i, j, time_coord='Time',south_north='south_north',west_east='west_east'):
    start = time.time()
    data = ws[:,i,j].load()
    hours = np.array(list(data.groupby(f'{time_coord}.hour').groups.keys()))
    months = np.array(list(data.groupby(f'{time_coord}.month').groups.keys()))
    years = np.array(list(data.groupby(f'{time_coord}.year').groups.keys()))

    hourly_values = np.zeros((2, len(data.groupby(f'{time_coord}.hour'))))
    for hour, hourly_data in enumerate(data.groupby(f'{time_coord}.hour')):
        shape, scale = weibull(hourly_data[1])
        hourly_values[:, hour] = shape, scale
    monthly_values = np.zeros((2, len(data.groupby(f'{time_coord}.month'))))
    for month, monthly_data in enumerate(data.groupby(f'{time_coord}.month')):
        shape, scale = weibull(monthly_data[1])
        monthly_values[:, month] = shape, scale
    yearly_values = np.zeros((2, len(data.groupby(f'{time_coord}.year'))))
    for year, yearly_data in enumerate(data.groupby(f'{time_coord}.year')):
        shape, scale = weibull(yearly_data[1])
        yearly_values[:, year] = shape, scale
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
    weibull_dataset['hour'] = hours
    weibull_dataset['month'] = months
    weibull_dataset['year'] = years
    weibull_dataset['parameter'] = ['shape', 'scale']
    weibull_dataset[south_north] = i
    weibull_dataset[west_east] = j

    return weibull_dataset

