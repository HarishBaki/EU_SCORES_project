import xarray as xr
import os, glob

def preprocess(ds):
    ds = ds.expand_dims(west_east=1, south_north=1)
    ds = ds.assign_coords(west_east=ds.west_east, south_north=ds.south_north)
    return ds

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
run = 'New_runs' #sys.argv[1]
case = 'Germany_coast' #sys.argv[2]
level = 80 #int(sys.argv[3])
target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files/weibull_{level}'
files = [f'{target_dir}/{i}_{j}.nc' for i in range(8) for j in range(63)]

ds = xr.open_mfdataset(files,combine='nested', parallel=True, preprocess=preprocess)
# ds.assign_coords(south_north=ds.south_north)
ds