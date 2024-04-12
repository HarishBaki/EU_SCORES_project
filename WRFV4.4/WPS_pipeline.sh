#!/bin/bash
# This script runs the WPS program for a specific namelist the main script loop.

root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
WPS_source_dir="$1"
case_dir="$2"
timestamp="$3"
grib_source_dir="$4"
year="$5"
month="$6"
WPS_dir="$7"

# instead of copying the WPS_source_dir, do rsync, so that only the changed files are copied.
rsync -av --exclude='namelist.wps' --exclude='Vtable' $WPS_source_dir/* .   # copy the WPS source files to the run directory
ln -sf $case_dir/geo_em.d0* .   # link the geogrid files to the run directory
cp $case_dir/namelist.wps .     # copy the namelist.wps file to the run directory
sed -i -e "s/ start_date =/ start_date =$timestamp, /g" namelist.wps    # change the start_date in the namelist.wps file
sed -i -e "s/ end_date =/ end_date =$timestamp, /g" namelist.wps    # change the end_date in the namelist.wps file

ln -sf "$root_dir/WRFV4.4/Vtable.CERRA" Vtable   # link the Vtable file to the run directory
sed -i -e "s/ prefix =/ prefix ='CERRA'/g" namelist.wps # change the prefix in the namelist.wps file
./link_grib.csh $grib_source_dir'/'$year'/CERRA_'$year'_'$month'_'* # link the grib files to the run directory
./ungrib.exe    # run the ungrib program

sed -i -e "s/ prefix ='CERRA'/ prefix ='ERA5'/g" namelist.wps # change the prefix in the namelist.wps file
ln -sf ungrib/Variable_Tables/Vtable.ERA-interim.pl Vtable # link the Vtable file to the run directory
./link_grib.csh '/media/harish/External_1/CERRA/'$year'/ERA5_'$year'_'$month'_'*    # link the grib files to the run directory
./ungrib.exe    # run the ungrib program
./metgrid.exe   # run the metgrid program
rm -r CERRA:*   # remove the CERRA files
rm -r ERA5:*    # remove the ERA5 files
rm -r GRIBFILE* # remove the GRIB files

mv met_em* $WPS_dir #   move the final processed files to the main WPS directory