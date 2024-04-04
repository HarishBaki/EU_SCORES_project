import xarray as xr
import os
import glob
import dask.distributed as dd
import dask
import dask.array as da
import time
import sys
import calendar
from datetime import datetime, timedelta
import numpy as np
import wrf
from itertools import product

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#matplotlib inline

plt.rcParams['text.usetex'] = False

import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FixedLocator, FixedFormatter

import cartopy
from cartopy import crs
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from matplotlib.cm import get_cmap
import cmaps

from windrose import WindroseAxes

from scipy.stats import weibull_min

import seaborn as sns
import seaborn.objects as so

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import AutoMinorLocator

from scipy.stats import linregress


from meteostat import Stations
from datetime import datetime
from meteostat import Hourly

from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.mixture import GaussianMixture
from sklearn.covariance import EllipticEnvelope

root_dir = '/media/harish/SSD_4TB/EU_SCORES'

# Extrapolating buoy wind to required height
def extrapolate(Um, Zm, Z0, Z):
    '''
    Um: Measured wind
    Zm: measured height
    Z0: Roughness length
    Z: reference height
    '''
    return Um*np.log(Z/Z0)/np.log(Zm/Z0)

# Writing a function to extract location wise data based on XLAT and XLONG
def read_pointwise_timeseries(ds, target_lat, target_lon, var_name = None,vert_levels=None):
    if 'Time' in ds.coords:
        # If 'Time' is present in the coordinates, select the first time step
        ds_single_time = ds.isel(Time=0)
    else:
        # If 'Time' is not present, use the dataset as is
        ds_single_time = ds
    start = time.time()
    # Calculate the squared distance to each grid point
    distance_squared = (ds_single_time.XLAT - target_lat)**2 + (ds_single_time.XLONG - target_lon)**2
    end = time.time()
    print(f'Time elapsed for nearest point identification is {end-start}s')
    # Find the indices of the nearest grid point
    indices = np.unravel_index(np.nanargmin(distance_squared), distance_squared.shape)
    nearest_indices = {'south_north': indices[0], 'west_east': indices[1]}
    print(nearest_indices)
    # Select the nearest point using the indices
    if var_name:
        if vert_levels:
            var_timeseries = ds[var_name].isel(bottom_top=slice(None,vert_levels),south_north=nearest_indices['south_north'], west_east=nearest_indices['west_east'])
        else:
            var_timeseries = ds[var_name].isel(south_north=nearest_indices['south_north'], west_east=nearest_indices['west_east'])
    else:
        if vert_levels:
            var_timeseries = ds.isel(bottom_top=slice(None,vert_levels),south_north=nearest_indices['south_north'], west_east=nearest_indices['west_east'])
        else:
            var_timeseries = ds.isel(south_north=nearest_indices['south_north'], west_east=nearest_indices['west_east'])
    var_timeseries.name = 'data'
    return var_timeseries

'''
for key in points1.keys():
    read_pointwise_timeseries(ws,points1[key][0],points1[key][1]).to_netcdf(f'{root_dir}/{key}_wind_speed.nc')
'''

chunks={"Time": -1,"south_north": 8,"west_east": 8}
def wind_speed(root_dir,var1,var2,level=None,chunks=None):
    if level:
        ds1 = xr.open_dataset(f'{root_dir}/{var1}_{level}.nc',chunks=chunks)
        ds2 = xr.open_dataset(f'{root_dir}/{var2}_{level}.nc',chunks=chunks)
    else:
        ds1 = xr.open_dataset(f'{root_dir}/{var1}.nc',chunks=chunks)
        ds2 = xr.open_dataset(f'{root_dir}/{var2}.nc',chunks=chunks)
    return np.sqrt(ds1[var1]**2+ds2[var2]**2)
def wind_direction(root_dir,var1,var2,level=None,chunks=None):
    if level:
        ds1 = xr.open_dataset(f'{root_dir}/{var1}_{level}.nc',chunks=chunks)
        ds2 = xr.open_dataset(f'{root_dir}/{var2}_{level}.nc',chunks=chunks)
    else:
        ds1 = xr.open_dataset(f'{root_dir}/{var1}.nc',chunks=chunks)
        ds2 = xr.open_dataset(f'{root_dir}/{var2}.nc',chunks=chunks)
    
    return np.mod(180+np.rad2deg(np.arctan2(ds1[var1], ds2[var2])),360)
def WPD(wind_speed):
    return 0.5*1.225*wind_speed**3

def turbine_power(wind,turbine_type=None):
    # Fix the spline approximation
    from scipy.interpolate import UnivariateSpline
    if turbine_type == '15MW':
        power_curve = pd.read_csv(f'{root_dir}/eval/IEA_15MW_240_RWT.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=3) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error
    elif turbine_type == '8MW':
        power_curve = pd.read_csv(f'{root_dir}/eval/2016CACost_NREL_Reference_8MW_180.csv', usecols=range(0, 2))
        spline = UnivariateSpline(power_curve.iloc[:,0],power_curve.iloc[:,1])
        power = spline(wind)
        power = xr.where(((wind>=4) & (wind<= 25)), power, 0)   #change it to np.where, if you encounter any error
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


def hexbin_plotter(gs,df0,df1,title,text_arg=None,units=None,xlabel=None,ylabel=None,colorbar=None,limits=None):
    
    txt0 = bias(df0,df1)
    txt1 = r(df0,df1)
    txt2 = RMSE(df0,df1)
    txt3 = MAE(df0,df1)
    txt4 = SI(df0,df1)
    txt5 = EMD(df0,df1)

    ax = fig.add_subplot(gs)
    hb = ax.hexbin(df0,df1, gridsize=100, bins='log', cmap='inferno')
    if text_arg:
        ax.text(0.05, 0.95, f'bias: {txt0:.2f} {units}\nr: {txt1:.2f}\nRMSE: {txt2:.2f} {units}\nMAE: {txt3:.2f} {units}\nSI: {txt4:.2f} %',
                      transform=ax.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),fontsize=14)
    
    if xlabel:
        ax.set_xlabel(xlabel,fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel,fontsize=14)
    ax.set_title(f'{title}',fontsize=14)
    ax.tick_params(labelsize=14)

    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.plot(np.linspace(limits[0],limits[1]),np.linspace(limits[0],limits[1]),'--',color='grey')
    
    if colorbar:
        cbar = fig.colorbar(hb, ax=ax, orientation='vertical')
        cbar.set_label('Log Count', fontsize=14)
        cbar.ax.tick_params(labelsize=14)
        
def hist_pdf_plotter(gs,dfs,bins,line_styles,colors,labels,xlabel=None,ylabel=None,title=None,text_arg=None,text_alignment=None):
    ax = fig.add_subplot(gs)
    for i,df in enumerate(dfs):
        sns.histplot(data=dfs[i], bins=bins, 
                             stat='density', color=colors[i], label=labels[i], linewidth=3,linestyle=line_styles[i],ax=ax,element='poly',fill=False)
        if i > 0:
            if text_arg:
                x_position = 0.65 if text_alignment == 'right' else 0.05
                txt5 = EMD(dfs[0], dfs[i])
                ax.text(x_position, 0.95-(i-1)*0.15, fr'EMD({labels[i]}): {txt5:.4f}',
                      transform=ax.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),fontsize=14)
    ax.set_xlabel(xlabel,fontsize=14)
    ax.set_ylabel(ylabel,fontsize=14)
    ax.set_title(title,fontsize=14)
    ax.tick_params(labelsize=14)
    return ax

def map_plotter(gs,data,x,y,levels,cmap,title,shrink,cbar_label,orientation,extent=None,rectangles=None,sample_points=None):    
    ax = fig.add_subplot(gs,projection=ccrs.PlateCarree())
    ax.coastlines()

    if levels is None:
        contour = data.plot.contourf(
        x=x,y=y,add_colorbar=False,cmap = cmap,extend='both',
        #cbar_kwargs = {'orientation':orientation, 'shrink':shrink, 'aspect':40, 'label':cbar_label,'fontsize':14},
        ax=ax)
    else:
        contour = data.plot.contourf(
        x=x,y=y,levels=levels,add_colorbar=False,cmap = cmap,extend='both',
        #cbar_kwargs = {'orientation':orientation, 'shrink':shrink, 'aspect':40, 'label':cbar_label,'fontsize':14},
        ax=ax)
    
    # Add colorbar with font size
    cbar = fig.colorbar(contour, orientation=orientation, shrink=shrink, aspect=40, label=cbar_label)
    cbar.ax.tick_params(labelsize=14)
    cbar.ax.set_xlabel(cbar_label, fontsize=14)
    
    if extent:
        # Set the extent (for example, bounding box for Europe)
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    # Add gridlines with labels
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    # Set x and y ticks font size
    gl.xlabel_style = {'size': 14}
    gl.ylabel_style = {'size': 14}
    
    # set title
    ax.set_title(title,fontsize=14)
    
    # Add land feature with grey color
    land_feature = cfeature.NaturalEarthFeature(
        'physical', 'land', '10m', edgecolor='face', facecolor='lightgrey'
    )
    ax.add_feature(land_feature)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1, edgecolor='black')
    
    if sample_points:
        for label, (lat, lon) in sample_points.items():
            ax.text(lon, lat - 0.05, label, color='black', fontsize=14, ha='center', va='center')
            ax.plot(lon, lat, '.', markersize=8,color='black')
        
    return ax

def variability_plotter(gs,data,title,xlabel,ylabel,label,color,marker,xlabel_ticks=None,legend=None):
    ax = fig.add_subplot(gs)
    #sns.lineplot(x=x, y=y, data=data, ax=ax,lw=2,label=label,legend=legend,color=color,marker=marker,markersize=8)
    
    for i, key in enumerate(data):
        sns.lineplot(x=data.index.name, y=key, data=data, ax=ax, lw=2, label=key, legend=legend, color=colors[i], marker=markers[i], markersize=8)
        ax.axhline(data[key].mean(), color=colors[i], linestyle='--', label=f'{key} Overall Mean')
    
    ax.set_title(title,fontsize=14)
    ax.set_xlabel(xlabel,fontsize=14)
    ax.set_ylabel(ylabel,fontsize=14)
    
    # Set x and y ticks font size
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)  

    # Set x-axis range
    ax.set_xlim([data.index.min(), data.index.max()])
    
    if xlabel_ticks is not None:
        ax.set_xticks(data.index)
        ax.set_xticklabels(xlabel_ticks)
    
    return ax

line_styles = ['-','--','-']
colors = [
    'black',  # Light Blue
    'orange',    # Dark Orange
    (102/255, 0/255, 102/255),     # Dark Purple
    (0/255, 153/255, 0/255),      # Dark Green
    (204/255, 0/255, 0/255),      # Dark Red
    (139/255, 69/255, 19/255),    # Saddle Brown
    (51/255, 51/255, 102/255)    # Dark Blue
]
markers = ['o','d','p','s','*','']

hours = list(np.arange(0, 24))
months = ['Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov']

from scipy import stats
from scipy.spatial import distance
def mean(df):
    return round(df.mean(),2)
def std(df):
    return round(df.std(),2)
def r(df1,df2):
    return round(np.corrcoef(df2,df1)[0,1],2)
def bias(df1,df2):
    return round((mean(df2)-mean(df1)),2)
def RMSE(df1,df2):
    return round((np.sqrt(((df2 - df1) ** 2).mean())),2)
def MAE(df1,df2):
    return round(np.mean(np.abs(df2-df1)),2)
def SI(df1,df2):
    return round((RMSE(df2, df1)*100/mean(df1)),2)

def EMD(df1,df2):
    bins = np.arange(0,25.1,0.1)
    hist1 = np.histogram(df1,bins,density=True)[0]
    hist2 = np.histogram(df2,bins,density=True)[0]
    #return stats.wasserstein_distance(bins[:-1],bins[:-1],u_weights=hist1,v_weights=hist2)
    
    return stats.wasserstein_distance(df1,df2)

all_sample_points = {}
all_sample_points['Portugal_coast'] = {
    "P1": (41.35, -8.9),
    "P2": (41.5236, -9.055), #P2 is POR2 in tslist
    "P3": (41.7, -9.2),
}
all_sample_points['Netherlands_coast'] = {
    "P1": (51.3, 2.3),
    "P2": (51.6, 2.6), #P2 is POR2 in tslist
    "P3": (51.75, 3.25),
}
all_sample_points['Ireland_coast'] = {
    "P1": (52.55,-10.25),
    "P2": (52.85, -10), #P2 is POR2 in tslist
    "P3": (52.9, -10.4),
}

if __name__ == "__main__":
    """
    # === Wind resources ===# 
    run='New_runs'
    chunks={"Time": -1,"south_north": 24,"west_east": 24}
    level_and_rated_power = [[120,8],[150,15]]
    for case in ['Portugal_coast','Ireland_coast','Netherlands_coast']:
        run_dir=f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files'
        sample_points = all_sample_points[case]
        for level,rated_power in level_and_rated_power:
            # --- start client ---#
            print("Starting parallel computing...")
            cluster = dd.LocalCluster(n_workers=24, dashboard_address=':22722')
            client = dd.Client(cluster)
            # --- source datasets ---#
            turbine_type = f'{rated_power}MW'
            ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']
            wpd = WPD(ws)
            tp = xr.open_dataset(f'{run_dir}/{turbine_type}/tp_{level}.nc',chunks=chunks)['power'] # in kW
            CF = (tp*1e2/(rated_power*1e3)).load() # in %
            print('Done data loading')
            '''
            # --- mean quantities ---#
            mean_ws = ws.mean(dim='Time').compute()
            mean_wpd = wpd.mean(dim='Time').compute()
            mean_AEP = tp.isel(Time=slice(None,-1)).resample(Time='Y').sum().mean(dim='Time').compute()
            mean_CF = mean_AEP*1e2/(8766*rated_power*1e3) # in %
            print('Done mean quantities')

            # --- plotting mean quantities ---#
            fig = plt.figure(figsize=(12, 11), constrained_layout=True)
            gs = fig.add_gridspec(2,2)
            map_plotter(gs[0,0],mean_ws[10:-10,10:-10],'XLONG','XLAT',None,'flare',f'Mean annual wind speed ({level}m)',1,'m/s','horizontal',sample_points = sample_points)
            map_plotter(gs[0,1],mean_wpd[10:-10,10:-10],'XLONG','XLAT',None,'crest',f'Mean annual WPD ({level}m)',1,'W/m^2','horizontal',sample_points = sample_points)
            map_plotter(gs[1,0],mean_AEP[10:-10,10:-10]/1e6,'XLONG','XLAT',None,"ch:s=-.2,r=.6",f'Mean AEP ({level}m, {turbine_type})',1,'GWh/year','horizontal',sample_points = sample_points)
            map_plotter(gs[1,1],mean_CF[10:-10,10:-10],'XLONG','XLAT',None,"ch:s=10,r=.6",f'Mean CF ({level}m, {turbine_type})',1,'%','horizontal',sample_points = sample_points)
            plt.savefig(f'{case}_optimization_runs_mean_wind_resources_{level}m_{turbine_type}.png',dpi=300,bbox_inches='tight',pad_inches=0)
            plt.close()
            print('Done mean quantities plotter')
            '''
            # --- plotting variabilities ---#
            fig = plt.figure(figsize=(12, 12), constrained_layout=True)
            gs = fig.add_gridspec(3,1)
            sns.set_theme(style="white")
            hourly_df = pd.DataFrame()
            for i,key in enumerate(sample_points.keys()):
                ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

                pointwise_df = pd.DataFrame()

                # Loop through hours
                for hour in range(0,24):
                    # Extract data for the current year
                    data = ds.sel(Time=ds.Time.dt.hour == hour).mean().values
                    # Create a new DataFrame with the year as a column
                    #df = pd.DataFrame({'Hour': [hour], key: data})
                    df = pd.DataFrame({key: data}, index=pd.Index([hour], name='Hour'))
                    # Append the data to the main DataFrame
                    pointwise_df = pd.concat([pointwise_df, df])
                hourly_df = pd.concat([hourly_df, pointwise_df],axis=1)

            variability_plotter(gs[0,0],hourly_df,f'Diurnal variability ({level}m, {turbine_type})','Hours','CF (%)', key,colors[i],'o',xlabel_ticks=hours)

            monthly_df = pd.DataFrame()
            for i,key in enumerate(sample_points.keys()):
                ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

                pointwise_df = pd.DataFrame()

                # Loop through hours
                for month in [12,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                    # Extract data for the current year
                    data = ds.sel(Time=ds.Time.dt.month == month).mean().values
                    # Create a new DataFrame with the year as a column
                    #df = pd.DataFrame({'Hour': [hour], key: data})
                    df = pd.DataFrame({key: data}, index=pd.Index([months[month-1]], name='month'))
                    # Append the data to the main DataFrame
                    pointwise_df = pd.concat([pointwise_df, df])
                monthly_df = pd.concat([monthly_df, pointwise_df],axis=1)

            variability_plotter(gs[1,0],monthly_df,f'Annual variability({level}m, {turbine_type})','Months','CF (%)', key,colors[i],'o',xlabel_ticks=months)

            yearly_df = pd.DataFrame()
            for i,key in enumerate(sample_points.keys()):
                ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

                pointwise_df = pd.DataFrame()

                # Loop through hours
                for year in list(range(1990, 2021)):
                    # Extract data for the current year
                    data = ds.sel(Time=ds.Time.dt.year == year).mean().values
                    # Create a new DataFrame with the year as a column
                    #df = pd.DataFrame({'Hour': [hour], key: data})
                    df = pd.DataFrame({key: data}, index=pd.Index([year], name='year'))
                    # Append the data to the main DataFrame
                    pointwise_df = pd.concat([pointwise_df, df])
                yearly_df = pd.concat([yearly_df, pointwise_df],axis=1)

            axs = variability_plotter(gs[2,0],yearly_df,f'Interannual variability ({level}m, {turbine_type})','Years','CF (%)', key,colors[i],'o')

            # Extract legend from one of the subplots
            handles, labels = axs.get_legend_handles_labels()
            # Create a common legend below the figures
            fig.legend(handles, labels, loc='lower center', ncol=len(labels), bbox_to_anchor=(0.5, -0.05),fontsize=14)
            plt.savefig(f'{case}_optimization_runs_CF_variabilities_{level}m_{turbine_type}.png',dpi=300,bbox_inches='tight',pad_inches=0)
            plt.close()
            
            # --- close client ---#
            client.close()
            cluster.close()
    """
    # === Solar resources ===# 
    Epv = 0.216
    cell_watt = 365
    run='New_runs'
    chunks={"Time": -1,"south_north": 24,"west_east": 24}
    for case in ['Portugal_coast','Ireland_coast','Netherlands_coast']:
        sample_points = all_sample_points[case]
        # --- start client ---#
        print("Starting parallel computing...")
        cluster = dd.LocalCluster(n_workers=48, dashboard_address=':22722')
        client = dd.Client(cluster)
        # --- source datasets ---#
        
        run_dir=f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files'
        XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc')
        XLAT = XLAND.XLAT
        XLONG = XLAND.XLONG
        t2m = xr.open_dataset(f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files/T2.nc',chunks=chunks)
        t2m = t2m['T2'].assign_coords(XLAT=XLAT,XLONG=XLONG)
        swdown = xr.open_dataset(f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files/SWDOWN2.nc',chunks=chunks)
        swdown = swdown['SWDOWN2'].assign_coords(XLAT=XLAT,XLONG=XLONG)
        spv = xr.open_dataset(f'{root_dir}/{run}/{case}/Postprocessed/variablewise_files/spv.nc',chunks=chunks)['PVO']
        CF = (spv*1e2/cell_watt).load()
        
        print('Done data loading')
        '''
        # --- mean quantities ---#
        mean_t2m = t2m.mean(dim='Time').compute()
        mean_swdown = swdown.mean(dim='Time').compute()
        mean_spv = spv.isel(Time=slice(None,-1)).resample(Time='Y').sum().mean(dim='Time').compute()
        mean_CF = CF.mean(dim='Time').compute()
        
        # --- plotting mean quantities ---#
        sample_points = all_sample_points[case]
        fig = plt.figure(figsize=(12, 9), constrained_layout=True)
        gs = fig.add_gridspec(2,2)
        map_plotter(gs[0,0],mean_t2m[10:-10,10:-10],'XLONG','XLAT',None,'flare',f'Mean annual 2m temperature',1,r'$^{\circ}$C','horizontal',sample_points = sample_points)
        map_plotter(gs[0,1],mean_swdown[10:-10,10:-10],'XLONG','XLAT',None,'crest',f'Mean annual SWDOWN',1,'W/m^2','horizontal',sample_points = sample_points)
        map_plotter(gs[1,0],mean_spv[10:-10,10:-10]/1e3,'XLONG','XLAT',None,"ch:s=-.2,r=.6",f'Mean AEP',1,'KW/year','horizontal',sample_points = sample_points)
        map_plotter(gs[1,1],mean_CF[10:-10,10:-10],'XLONG','XLAT',None,"ch:s=10,r=.6",f'Mean CF',1,'%','horizontal',sample_points = sample_points)
        plt.savefig(f'{case}_optimization_runs_mean_solar_resources.png',dpi=300,bbox_inches='tight',pad_inches=0)
        plt.close()
        print('Done mean quantities plotter')
        '''
        # --- plotting variabilities ---#
        fig = plt.figure(figsize=(12, 12), constrained_layout=True)
        gs = fig.add_gridspec(3,1)
        sns.set_theme(style="white")

        hourly_df = pd.DataFrame()
        for i,key in enumerate(sample_points.keys()):
            ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

            pointwise_df = pd.DataFrame()

            # Loop through hours
            for hour in range(0,24):
                # Extract data for the current year
                data = ds.sel(Time=ds.Time.dt.hour == hour).mean().values
                # Create a new DataFrame with the year as a column
                #df = pd.DataFrame({'Hour': [hour], key: data})
                df = pd.DataFrame({key: data}, index=pd.Index([hour], name='Hour'))
                # Append the data to the main DataFrame
                pointwise_df = pd.concat([pointwise_df, df])
            hourly_df = pd.concat([hourly_df, pointwise_df],axis=1)

        variability_plotter(gs[0,0],hourly_df,f'Diurnal variability','Hours','CF (%)', key,colors[i],'o',xlabel_ticks=hours)


        monthly_df = pd.DataFrame()
        for i,key in enumerate(sample_points.keys()):
            ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

            pointwise_df = pd.DataFrame()

            # Loop through hours
            for month in [12,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                # Extract data for the current year
                data = ds.sel(Time=ds.Time.dt.month == month).mean().values
                # Create a new DataFrame with the year as a column
                #df = pd.DataFrame({'Hour': [hour], key: data})
                df = pd.DataFrame({key: data}, index=pd.Index([months[month-1]], name='month'))
                # Append the data to the main DataFrame
                pointwise_df = pd.concat([pointwise_df, df])
            monthly_df = pd.concat([monthly_df, pointwise_df],axis=1)

        variability_plotter(gs[1,0],monthly_df,f'Annual variability','Months','CF (%)', key,colors[i],'o',xlabel_ticks=months)

        yearly_df = pd.DataFrame()
        for i,key in enumerate(sample_points.keys()):
            ds = read_pointwise_timeseries(CF,sample_points[key][0],sample_points[key][1])

            pointwise_df = pd.DataFrame()

            # Loop through hours
            for year in list(range(1990, 2021)):
                # Extract data for the current year
                data = ds.sel(Time=ds.Time.dt.year == year).mean().values
                # Create a new DataFrame with the year as a column
                #df = pd.DataFrame({'Hour': [hour], key: data})
                df = pd.DataFrame({key: data}, index=pd.Index([year], name='year'))
                # Append the data to the main DataFrame
                pointwise_df = pd.concat([pointwise_df, df])
            yearly_df = pd.concat([yearly_df, pointwise_df],axis=1)

        axs = variability_plotter(gs[2,0],yearly_df,f'Interannual variability','Years','CF (%)', key,colors[i],'o')

        # Extract legend from one of the subplots
        handles, labels = axs.get_legend_handles_labels()
        # Create a common legend below the figures
        fig.legend(handles, labels, loc='lower center', ncol=len(labels), bbox_to_anchor=(0.5, -0.05),fontsize=14)
        plt.savefig(f'{case}_optimization_runs_solar_resources_variabilities.png',dpi=300,bbox_inches='tight',pad_inches=0)
        plt.close()
        # --- close client ---#
        client.close()
        cluster.close()
