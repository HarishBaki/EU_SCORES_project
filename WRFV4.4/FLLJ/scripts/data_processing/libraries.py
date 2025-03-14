import xarray as xr
import pandas as pd
import numpy as np
from scipy.stats import weibull_min
import time
import glob

root_dir = '/media/ssd_4tb_qvo/EU_SCORES_project/WRFV4.4/FLLJ/'
domains = ['d03', 'd02', 'd02', 'd02','d01','d02','d01','d03','d02', 'd02', 'd02','d01','d02','d01','d01','d01','d01']
event_periods = [['2016-02-21T18:00','2016-02-22T18:00'],['2016-03-03T18:00','2016-03-04T18:00'],
                 ['2016-02-09-T00:00','2016-02-10-T00:00'],['2017-01-09-T12:00','2017-01-10-T12:00'],
                 ['2017-01-29-T18:00','2017-01-30-T18:00']] # don't put seconds in the time string
ramp_periods = [['2016-02-22T01:00','2016-02-22T12:00'],['2016-03-04T01:00','2016-03-04T12:00'],
                ['2016-02-09-T01:00','2016-02-09-T12:00'],['2017-01-09-T19:00','2017-01-10-T06:00'],
                 ['2017-01-30-T01:00','2017-01-30-T12:00']]

run_names = ['ERA5-3d1kmMYFP',
             'CERRA-2d1kmMYFP','CERRA-2d1kmMYnoFP','CERRA-2d1kmSH','CERRA-1d1kmMYFP','CERRA-2d0.5kmSH','CERRA-1d0.5kmSH',
             'GFS-3d1kmMYFP',
             'CERRA-2d1kmMYFP','CERRA-2d1kmMYnoFP','CERRA-2d1kmSH','CERRA-1d1kmMYFP','CERRA-2d0.5kmSH','CERRA-1d0.5kmSH',
             'CERRA-1d1kmSH',
             'CERRA-1d1kmMYFP_100_levels','CERRA-1d1kmMYFP_12hr_spinup']

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


# For the 8th simulation of FLLJ_1, the data is taken from uvmet_interp.nc file
def extract_u_v(root_dir, case_dir,run, run_dir,dates_range=None,levels=None,location=None):
    '''
    root_dir: str, root directory of the WRF output files
    case_dir: str, case directory
    run: int, run number
    dates_range: list of two datetime objects, range of dates to extract, or a single datetime object 
    levels: list of two integers, range of vertical levels to extract, or a single integer
    location: list of two floats, latitude and longitude of the location to extract
    '''
    from scipy.interpolate import interp1d
    if (case_dir == 'FLLJ_1' and run == 8):
        file = glob.glob(f'{root_dir}/{case_dir}/{run_dir}/uvmet_interp*')[0]
        chunks={"Time": 1,"south_north": -1,"west_east": -1}
        ds = xr.open_dataset(file,chunks=chunks)
        # Extract XLONG and XLAT coordinates
        XLONG = ds.XLONG.values
        XLAT = ds.XLAT.values
        z = ds.level.values

        if dates_range is not None:
            if isinstance(dates_range,list):
                ds = ds.sel(Time=slice(*dates_range))
            else:
                ds = ds.sel(Time=dates_range)
        Times = ds.Time
        if location is not None:
            ind_y,ind_x = find_nearest_indice(XLAT, XLONG, location[0],location[1])
            ds = ds.isel(south_north=ind_y,west_east=ind_x)

        u_data = ds.uvmet_interp.sel(u_v='u')
        v_data = ds.uvmet_interp.sel(u_v='v')

        if levels is not None:
            if isinstance(levels,list):
                u_data = u_data.sel(level=slice(*levels))
                v_data = v_data.sel(level=slice(*levels))
            else:
                # check if levels exist in z
                if levels in z:
                    u_data = u_data.sel(level=levels)
                    v_data = v_data.sel(level=levels)
                else:
                    u_data = u_data.interp(level=levels,method='linear')
                    v_data = v_data.interp(level=levels,method='linear')
    else:
        file = glob.glob(f'{root_dir}/{case_dir}/{run_dir}/auxhist22_{domains[run-1]}*')[0]
        chunks={"Time": 1,"south_north": -1,"west_east": -1}
        ds = xr.open_dataset(file,chunks=chunks)
        Times = pd.to_datetime(np.char.decode(ds.Times, 'utf-8'), format='%Y-%m-%d_%H:%M:%S')
        z = ds.Z_ZL[0,...].values
        ds = ds.assign_coords(Time=Times,num_z_levels_stag=z)
        # Extract XLONG and XLAT coordinates
        XLONG = ds.XLONG[0,...].values
        XLAT = ds.XLAT[0,...].values

        if dates_range is not None:
            if isinstance(dates_range,list):
                ds = ds.sel(Time=slice(*dates_range))
            else:
                ds = ds.sel(Time=dates_range) 
        Times = ds.Time
        if location is not None:
            ind_y,ind_x = find_nearest_indice(XLAT, XLONG, location[0],location[1])
            ds = ds.isel(south_north=ind_y,west_east=ind_x)

        # Extract the data at the specified time and vertical level
        u_data = ds.U_ZL
        v_data = ds.V_ZL

        if levels is not None:
            if isinstance(levels,list):
                u_data = u_data.sel(num_z_levels_stag=slice(*levels))
                v_data = v_data.sel(num_z_levels_stag=slice(*levels))
            else:
                if levels in z:
                    u_data = u_data.sel(num_z_levels_stag=levels)
                    v_data = v_data.sel(num_z_levels_stag=levels)
                else:
                    u_data = u_data.interp(num_z_levels_stag=levels,method='linear')
                    v_data = v_data.interp(num_z_levels_stag=levels,method='linear')
    
    return u_data, v_data, XLONG, XLAT

def wind_speed(ds1,ds2):
    '''
    ds1: xarray DataArray of u-component of wind
    ds2: xarray DataArray of v-component of wind
    returns ws: xarray DataArray of wind speed, magnitude in m/s
    ''' 
    ws = xr.DataArray(np.sqrt(ds1**2 + ds2**2), name='ws')
    return ws 

def wind_direction(ds1,ds2):
    '''
    ds1: xarray DataArray of u-component of wind
    ds2: xarray DataArray of v-component of wind
    returns wd: xarray DataArray of wind direction in degrees
    calculated from https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398
    ''' 
    wd = xr.DataArray(np.mod(180+np.rad2deg(np.arctan2(ds1, ds2)),360), name='wdir')
    return wd

# Read in the text file containing location and turbine type information
data = pd.read_csv(f"{root_dir}/windturbines.txt", delim_whitespace=True,header=None)
turbine_lats = data.iloc[:,0].to_numpy()
turbine_lons = data.iloc[:,1].to_numpy()
turbine_types = data.iloc[:,2].to_numpy()
# Define the power curves of the turbine types as lists of tuples
power_curve_type_1 = pd.read_csv(f"{root_dir}/wind-turbine-1.tbl",delim_whitespace=True,skiprows=2,header=None,usecols=[0,2])
power_curve_type_2 = pd.read_csv(f"{root_dir}/wind-turbine-2.tbl",delim_whitespace=True,skiprows=2,header=None,usecols=[0,2])
power_curve_type_3 = pd.read_csv(f"{root_dir}/wind-turbine-3.tbl",delim_whitespace=True,skiprows=2,header=None,usecols=[0,2])
power_curve_type_4 = pd.read_csv(f"{root_dir}/wind-turbine-4.tbl",delim_whitespace=True,skiprows=2,header=None,usecols=[0,2])
power_curve_type_5 = pd.read_csv(f"{root_dir}/wind-turbine-5.tbl",delim_whitespace=True,skiprows=2,header=None,usecols=[0,2])
hub_heights = [71,72,94,94,100]
power_curves = [power_curve_type_1,power_curve_type_2,power_curve_type_3,power_curve_type_4,power_curve_type_5]

def turbine_power(wind,power_curve):
    '''
    wind: xarray DataArray of wind speed
    turbine_type: str, type of turbine, either '15MW' or '8MW'
    returns power: xarray DataArray of power, in KW
    '''
    # Fix the spline approximation
    from scipy.interpolate import UnivariateSpline
    spline = UnivariateSpline(power_curve[:,0],power_curve[:,1])
    power = spline(wind)
    power = xr.where(((wind>=power_curve[0, 0]) & (wind<= power_curve[-1, 0])), power, 0)   #change it to np.where, if you encounter any error
    return xr.DataArray(power,name='power')

def extract_POWER(root_dir, case_dir,run, run_dir,dates_range=None):
    file = glob.glob(f'{root_dir}/{case_dir}/{run_dir}/wrfout_{domains[run-1]}*')[0]
    chunks={"Time": 1,"south_north": -1,"west_east": -1}
    ds = xr.open_dataset(file,chunks=chunks)
    Times = pd.to_datetime(np.char.decode(ds.Times, 'utf-8'), format='%Y-%m-%d_%H:%M:%S')
    ds = ds.assign_coords(Time=Times)
    if dates_range is not None:
        if isinstance(dates_range,list):
            ds = ds.sel(Time=slice(*dates_range))
        else:
            ds = ds.sel(Time=dates_range) 
    POWER = ds.POWER.sum(dim='south_north').sum(dim='west_east')
    return POWER

def D(O,M):
    '''
    O: observed data
    M: model data
    returns the difference between the observed and model data
    '''
    return (M-O)

def NRMSE(O,M):
    '''
    O: observed data
    M: model data
    returns the normalized root mean square error
    '''
    RMSE = np.sqrt(np.mean(D(O,M)**2))
    var1 = np.var(O)
    var2 = np.var(M)
    return RMSE/np.sqrt(var1+var2)

def NBIAS(O,M):
    '''
    O: observed data
    M: model data
    returns the normalized bias
    '''
    return np.mean(D(O,M))/np.std(D(O,M))

def NEV(O,M):
    '''
    O: observed data
    M: model data
    returns the normalized error variance
    '''
    var1 = np.var(O)
    var2 = np.var(M)
    return (np.var(D(O,M)))/(var2+var1)

def NPE(O,M):
    '''
    O: observed data
    M: model data
    returns the normalized pattern error, which is the sqrt of the normalized error variance
    '''
    return np.sqrt(NEV(O,M))

def rho(O,M):
    '''
    O: observed data
    M: model data
    returns the correlation coefficient, implying a phase error
    '''
    return np.corrcoef(O,M)[0,1]

def eta(O,M):
    '''
    O: observed data
    M: model data
    returns the amplitude error
    '''
    var1 = np.var(O)
    var2 = np.var(M)
    return (np.sqrt(var1*var2))/(0.5*(var1+var2))

def Taylor_Skill_Score(O,M):
    std1 = np.std(O)
    std2 = np.std(M)
    SDR = std2/std1
    CC = np.corrcoef(O,M)[0,1]
    return 4*(1+CC)**2/((1+0.99999)**2*((SDR+(1/SDR))**2))

def T_metric(O,M):
    '''
    O: observed data
    M: model data
    returns the T-metric
    https://journals.ametsoc.org/view/journals/hydr/18/10/jhm-d-17-0045_1.xml?tab_body=abstract-display
    '''
    R = np.corrcoef(O,M)[0,1]
    MSE = np.mean(D(O,M)**2)
    bias = np.mean(D(O,M))
    std1 = np.std(O)
    std2 = np.std(M)

    T = ((1+R)/2)*(1-(MSE/(bias**2+std1**2+std2**2)))

    return T
