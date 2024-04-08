import xarray as xr
import os, glob, sys
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import seaborn as sns
import seaborn.objects as so

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'

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

CERRA_target_grids = {'Iberia': {'min_lat': 41.25, 'min_lon': -9.35,'max_lat':41.8,'max_lon':-8.65},
           'Ireland': {'min_lat': 52.49, 'min_lon': -10.51,'max_lat':53,'max_lon':-9.7},
           'BeNeLux': {'min_lat': 50.95, 'min_lon': 2.25,'max_lat':51.8,'max_lon':3.55}}

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
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def map_plotter(fig,gs,data,x,y,levels,cmap,title,cbar_args,extent=None,rectangles=None,sample_points=None):    
    ax = fig.add_subplot(gs,projection=ccrs.PlateCarree())
    ax.coastlines()

    contour = data.plot.contourf(
        x=x,y=y,levels=levels,add_colorbar=False,cmap = cmap,extend='both',
        #cbar_kwargs = {'orientation':orientation, 'shrink':shrink, 'aspect':40, 'label':cbar_label,'fontsize':14},
        ax=ax)
    
    # Add colorbar with font size
    if cbar_args is not None:
        cbar = fig.colorbar(contour, orientation=cbar_args['orientation'], shrink=cbar_args['shrink'], aspect=40, label=cbar_args['cbar_label'])
        cbar.ax.tick_params(labelsize=14)
        cbar.ax.set_xlabel(cbar_args['cbar_label'], fontsize=14)
    
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

def variability_plotter(fig,gs,data,mean_data,title,xlabel,ylabel,label,color,marker,xlabel_ticks=None,legend=None):
    ax = fig.add_subplot(gs)
    #sns.lineplot(x=x, y=y, data=data, ax=ax,lw=2,label=label,legend=legend,color=color,marker=marker,markersize=8)
    
    for i, key in enumerate(data):
        sns.lineplot(x=data.index.name, y=key, data=data, ax=ax, lw=2, label=key, legend=legend, color=colors[i], marker=markers[i], markersize=8)
        if isinstance(mean_data,pd.DataFrame):
            ax.axhline(mean_data[key].values, color=colors[i], linestyle='--', label=f'{key} 31 years')
        else:
            ax.axhline(data[key].mean(), color=colors[i], linestyle='--', label=f'{key} 31 years')
    
    if title is not None:
        ax.set_title(title,fontsize=14)
    if xlabel is not None:
        ax.set_xlabel(xlabel,fontsize=14)
    if ylabel is not None:
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

def power_profile_plotter(fig,gs,data,title,xlabel,ylabel,label,color,marker,xlabel_ticks=None,legend=None):
    ax = fig.add_subplot(gs)
    #sns.lineplot(x=x, y=y, data=data, ax=ax,lw=2,label=label,legend=legend,color=color,marker=marker,markersize=8)
    
    for i, key in enumerate(data):
        sns.lineplot(x=data.index.name, y=key, data=data, ax=ax, lw=2, label=key, legend=legend, color=colors[i], marker=markers[i], markersize=8)
    
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

def calculate_color_levels(data, threshold=2):
    """
    Calculate color levels based on the range of data with different criteria.
    
    Parameters:
        data (array-like): The data array.
        threshold (float): The threshold to consider when calculating levels.
        
    Returns:
        levels (ndarray): The calculated levels for the color map.
    """
    data_min = np.min(data)
    data_max = np.max(data)
    data_range = data_max - data_min
    
    # Check the data range and set levels accordingly
    if data_range > 100:
        # Set levels at 10 multiples, no decimals
        num = 10
        min_value = np.floor(data_min / num) * num
        max_value = np.ceil(data_max / num) * num
        levels = np.arange(min_value, max_value + num, num)

    elif 20 < data_range < 100:
        # Set levels at multiples of 5, no decimals
        num = 5
        min_value = np.floor(data_min / num) * num
        max_value = np.ceil(data_max / num) * num
        levels = np.arange(min_value, max_value + num, num)

    elif 10 < data_range < 20:
        # Set levels at multiples of 1, no decimals
        num = 1
        min_value = np.floor(data_min / num) * num
        max_value = np.ceil(data_max / num) * num
        levels = np.arange(min_value, max_value + num, num)
    
    elif threshold < data_range < 10:
        # Set levels at multiples of 1, no decimals
        num = 0.5
        min_value = np.floor(data_min / num) * num
        max_value = np.ceil(data_max / num) * num
        levels = np.arange(min_value, max_value + num, num)

    else:
        # Set levels at multiples of 0.1, up to 2 decimals
        num = 0.1
        min_value = np.floor(data_min / num) * num
        max_value = np.ceil(data_max / num) * num
        levels = np.arange(min_value, max_value + num, num)

    return levels