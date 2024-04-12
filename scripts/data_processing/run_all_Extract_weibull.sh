#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
cases=('Germany_coast' 'Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
levels=(10 80 100 120 150)

south_north_grids=(63 127 127 199)
west_east_grids=(63 127 127 199)
# Loop over cases
for ((case_index=1; case_index<${#cases[@]}; case_index++)); do
    case="${cases[$case_index]}"

    south_north="${south_north_grids[$case_index]}"
    west_east="${west_east_grids[$case_index]}"
    
    # Loop over levels
    for level in "${levels[@]}"; do
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/ws_$level/weibull"
        for time_scale in 'season'; do
            # Loop over i and j indices to extract weibull parameters.
            # The catch is the number of processes that can be run in parallel are set to 98.
            count=0
            for ((i=0; i<$south_north; i++)); do
                for ((j=0; j<$west_east; j++)); do
                    count=$((count+1))
                    echo "Processing $case, $level, $i, $j"
                    python "$root_dir/scripts/data_processing/Extract_wind_weibull.py" "$run" "$case" "$level" "$i" "$j" "$time_scale" &
                    if [ $count -eq 96 ]; then
                        echo "Processing waits at $i, $j"
                        wait
                        count=0
                    fi
                done
            done
            wait
            
            # Combine the weibull parameters along individual south_north direciton and all west_east direction.
            count=0
            for ((i=0; i<$south_north; i++)); do
                python "$root_dir/scripts/data_processing/Combine_weibull.py" "$run" "$case" "$level" "$i" "0" "0" "$west_east" "$time_scale" &
                count=$((count+1))
                if [ $count -eq 96 ]; then
                    echo "Processing waits at $i"
                    wait
                    count=0
                fi
            done
            wait
            
            # Combine the weibull parameters along all directions and assign XLAT and XLONG coordinates.
            python "$root_dir/scripts/data_processing/Combine_weibull.py" "$run" "$case" "$level" "0" "0" "$south_north" "0" "$time_scale" 
        done
        # Remove the individual weibull files.
        rm -r "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/ws_$level/weibull"
        
    done
done
wait

echo "Script execution complete."
