#!/bin/bash

root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
runs=('New_runs' 'Validation_runs')
cases=('Netherlands_coast' 'Germany_coast' 'Portugal_coast' 'Ireland_coast')

run='New_runs'
case="Netherlands_coast"

: '
# the following script copies the intermediate files of WRF runs from the server to the local machine
files=( )
for i in {1..2265}; do
	files[${#files[*]}]="WRF_$i.nc"
done
printf "%s\n" "${files[@]}" > files.txt

rclone copy --progress --transfers 12 --files-from files.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/EU_SCORES_project/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/intermediate_files $root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/intermediate_files/.

# the following script copies the intermediate files of tslist from the server to the local machine
'

files=( )
for i in {1900..2046}; do
	#files[${#files[*]}]="LOT1_TS_$i.csv"
	files[${#files[*]}]="LOT2_UU_$i.csv"
	files[${#files[*]}]="LOT2_VV_$i.csv"
done
printf "%s\n" "${files[@]}" > files.txt

rclone copy --progress --transfers 12 --files-from files.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/EU_SCORES_project/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/intermediate_files $root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/intermediate_files/.

