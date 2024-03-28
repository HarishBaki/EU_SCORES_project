import xarray as xr
import sys, os, glob, time

def preprocess(ds):
    ds = ds.expand_dims(west_east=1, south_north=1)
    ds = ds.assign_coords(west_east=ds.west_east, south_north=ds.south_north)
    return ds

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'
run = sys.argv[1]
case = sys.argv[2]
level = int(sys.argv[3])
i = int(sys.argv[4])
j = int(sys.argv[5])
south_north_grids = int(sys.argv[6])
west_east_grids = int(sys.argv[7])

print(run,case,level,i,j,south_north_grids,west_east_grids)

run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'
target_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/statistics_files/ws_{level}'

if west_east_grids:
    start = time.time()
    files = [f'{target_dir}/weibull/{i}_{j}.nc' for j in range(west_east_grids)]
    ds = xr.open_mfdataset(files,combine='nested', parallel=True, preprocess=preprocess)
    ds.to_netcdf(f'{target_dir}/weibull/{i}.nc')
    print(f'{i} done in {time.time()-start} seconds')

if south_north_grids:
    start = time.time()
    files = [f'{target_dir}/weibull/{i}.nc' for i in range(south_north_grids)]
    ds = xr.open_mfdataset(files,combine='nested', parallel=True, concat_dim='south_north')

    XLAND = xr.open_dataset(f'{run_dir}/XLAND.nc')
    XLAT = XLAND.XLAT
    XLONG = XLAND.XLONG

    ds = ds.assign_coords(XLAT=XLAT, XLONG=XLONG)
    ds.to_netcdf(f'{target_dir}/weibull.nc')
    print(f'{level} done in {time.time()-start} seconds')

