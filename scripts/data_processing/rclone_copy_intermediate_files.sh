#!/bin/bash
case="Netherlands_coast"

files=( )
for i in {1..2265}; do
	files[${#files[*]}]="WRF_$i.nc"
done
printf "%s\n" "${files[@]}" > files.txt

rclone copy --progress --transfers 12 --files-from files.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/New_runs/$case/Postprocessed/intermediate_files intermediate_files/.

: '
files=( )
for i in {1..2265}; do
	files[${#files[*]}]="POR2_TS_$i.csv"
	files[${#files[*]}]="POR2_UU_$i.csv"
	files[${#files[*]}]="POR2_VV_$i.csv"
done
printf "%s\n" "${files[@]}" > files.txt

rclone copy --progress --transfers 12 --files-from files.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/New_runs/$case/Postprocessed/intermediate_files intermediate_files/.
'
