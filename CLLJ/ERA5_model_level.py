#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

c.retrieve("reanalysis-era5-complete", {
    "class": "ea",
    "date": "2007-08-19/to/2007-08-21",
    "expver": "1",
    "levelist": "117/118/119/120/121/122/123/124/125/126/127/128/129/130/131/132/133/134/135/136/137",
    "levtype": "ml",
    "param": "129/130/131/132/133/152",
    "stream": "oper",
    "time": "00:00:00/01:00:00/02:00:00/03:00:00/04:00:00/05:00:00/06:00:00/07:00:00/08:00:00/09:00:00/10:00:00/11:00:00/12:00:00/13:00:00/14:00:00/15:00:00/16:00:00/17:00:00/18:00:00/19:00:00/20:00:00/21:00:00/22:00:00/23:00:00",
    "type": "an",
    "area": "60.00/-20.00/40.00/20.00",
    "grid": "0.25/0.25",
    "format": "netcdf",
}, "ERA5-ml-u-v-t-subarea.nc")
