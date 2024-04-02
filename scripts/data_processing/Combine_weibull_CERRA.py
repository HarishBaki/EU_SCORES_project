import xarray as xr
import sys, os, glob, time

def preprocess(ds):
    ds = ds.expand_dims(x=1, y=1)
    ds = ds.assign_coords(x=ds.x, y=ds.y)
    return ds

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
region = sys.argv[1]
level = int(sys.argv[2])
i = int(sys.argv[3])
j = int(sys.argv[4])
south_north_grids = int(sys.argv[5])
west_east_grids = int(sys.argv[6])

print(region,level,i,j,south_north_grids,west_east_grids)

run_dir = f'{root_dir}/CERRA'
target_dir=f'{run_dir}/{region}/statistics_files/ws{level}'

if west_east_grids:
    start = time.time()
    files = [f'{target_dir}/weibull/{i}_{j}.nc' for j in range(west_east_grids)]
    ds = xr.open_mfdataset(files,combine='nested', parallel=True, preprocess=preprocess)
    # remove if file exist
    target_file = f'{target_dir}/weibull/{i}.nc'
    if os.path.exists(target_file):
        os.remove(target_file)
    ds.to_netcdf(target_file)
    print(f'{i} done in {time.time()-start} seconds')

if south_north_grids:
    start = time.time()
    files = [f'{target_dir}/weibull/{i}.nc' for i in range(south_north_grids)]
    ds = xr.open_mfdataset(files,combine='nested', parallel=True, concat_dim='y')

    latitude = xr.open_dataset(f'{run_dir}/{region}/variablewise_files/latitude.nc')
    longitude = xr.open_dataset(f'{run_dir}/{region}/variablewise_files/longitude.nc')
    ds.assign_coords(latitude=latitude['latitude'],longitude=longitude['longitude']).to_netcdf(f'{target_dir}/weibull.nc')
    
    print(f'{level} done in {time.time()-start} seconds')

