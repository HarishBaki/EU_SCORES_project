#!/bin/bash
# This script runs the WPS program for all the regions in a sequnce. 
# It runs one hour at a time, to minimize the computational load on the system.
# Geogrid files are already created before (ideally), thus will be linked, instead of rerunning.
# One speciality of this script is that, it will run WPS at every 3 hours in parallel, to save time. 
# Every three hours we chose because, the CERRA driving data available at every 3 hours.
# Since our aim is to gather the final processed files from the WPS program, we will create the WPS directories with a . in the beginning, so that they are hidden and not clutter the main directory.
# After finishing the WPS program, the final processed files will be moved to the main WPS directory, and the executable WPS directories will be deleted.

# starting and ending dates for the simulation are defined here.
start_date="1989-12-31"  
end_date="1989-12-31"

# with in these two dates, a loop increments the dates by 1 day. 
# Another loop runs WPS at every 3 hours, starting from 00 hours to 21 hours.

root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
case='Portugal_coast'    # cases are the names of regions we are simulating, e.g. 'Germany_coast' 'Portugal_coast' 'Ireland_coast' 'Netherlands_coast'
case_dir="$root_dir/WRFV4.4/EU_SCORES/New_runs/$case"
WPS_dir="$case_dir/WPS"
mkdir -p $WPS_dir
WPS_source_dir=/media/sukanta/HD2/WRF/WRFV4.4/WPS # this is the WPS installation directory
grib_source_dir='/media/harish/External_1/CERRA' # this is the directory where the CERRA driving data is stored, should be changed accordingly.

TZ=UTC  # setting the time zone to UTC
# loop between the start_date and end_dates at every 1 day increment
date=$start_date
while [ $(date -d "$date" +%s) -le $(date -d "$end_date" +%s) ]
do
    year=$(date -d "$date" '+%Y') # extract the year from the date
    month=$(date -d "$date" '+%m') # extract the month from the date
    day=$(date -d "$date" '+%d')   # extract the day from the date
    # these three will not change with in the hour loop, Thus, they are extracted prior.
    # loop between 00 hours to 21 hours at every 3 hours increment
    for hour in {0..23..3}
    do
        # based on the date and hour, create a timestamp in the format $year'-'$month'-$day_$hour:00:00'
        timestamp=$(TZ=$TZ date -d "$date $hour:00:00" '+%Y-%m-%d_%H:00:00')
        echo $day $timestamp
        
        run_dir="$case_dir/.WPS_$hour"   
        mkdir -p $run_dir
        cd $run_dir
            # Call the WPS pipeline here
            bash $root_dir/WRFV4.4/WPS_pipeline.sh $WPS_source_dir $case_dir $timestamp $grib_source_dir $year $month $WPS_dir &
        cd ..
    done
    date=$(date -d "$date + 1 day" '+%Y-%m-%d') # increment the date by 1 day
    wait
done
