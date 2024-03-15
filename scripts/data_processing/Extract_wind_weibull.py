import xarray as xr
import numpy as np
import sys
from scipy.stats import weibull_min

root_dir = '/media/harish/SSD_4TB/EU_SCORES_project'

run = 'New_runs' #sys.argv[1]
case = 'Germany_coast' #sys.argv[2]
level = '10' #int(sys.argv[3])

run_dir=f'{root_dir}/WRFV4.4/EU_SCORES/{run}/{case}/Postprocessed/variablewise_files'

chunks={"Time": 240,"south_north": -1,"west_east": -1}
ws = xr.open_dataset(f'{run_dir}/ws_{level}.nc',chunks=chunks)['ws']

print(ws.shape)

