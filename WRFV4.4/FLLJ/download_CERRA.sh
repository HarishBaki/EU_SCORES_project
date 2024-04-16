root_dir='/media/harish/SSD_4TB/EU_SCORES_project/WRFV4.4/FLLJ'
start_dates=('2016-02-21 14' '2016-03-03 12')
end_dates=('2016-02-22 18' '2016-03-04 18')
cases=('FLLJ_1' 'FLLJ_2')
cdsapirc_files=('/home/harish/.cdsapirc' '/home/harish/.cdsapirc2' '/home/harish/.cdsapirc3' '/home/harish/.cdsapirc_Max' '/home/harish/.cdsapirc_Sukanta' '/home/harish/.cdsapirc_Sandhya')
num_cdsapirc=${#cdsapirc_files[@]}
for (( i=0; i<${#cases[@]}; i++ ));
do
    case=${cases[i]}
    echo $case
    grib_source_dir=$root_dir/$case/Input_DATA/CERRA
    cd $grib_source_dir
        # loop over dates and times
        start_date=${start_dates[i]}
        end_date=${end_dates[i]}
        current_date=$start_date
        counter=0
        while [ $(date -ud "$current_date" +%s) -le $(date -ud "$end_date" +%s) ]; do
            year=$(date -ud "$current_date" +"%Y")
            month=$(date -ud "$current_date" +"%m")
            day=$(date -ud "$current_date" +"%d")
            hour=$(date -ud "$current_date" +"%H")
            cdsapirc_file=${cdsapirc_files[counter]}
            if [ $((10#$hour % 3)) -ne 0 ]; then  # Exclude hours divisible by 3
                echo $cdsapirc_file $year $month $day $hour
                python $root_dir/CERRA_convert_ERA5.py $cdsapirc_file $year $month $day $hour &
                counter=$(( (counter + 1) % num_cdsapirc ))  # Increment counter cyclically
                if [ $counter -eq 0 ]; then
                    wait  # Wait for every 6 concurrent runs
                fi
            fi
            current_date=$(date -ud "$current_date + 1 hour" +"%Y-%m-%d %H")
        done
    cd $root_dir
done