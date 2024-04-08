#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'

# extracting wind weibull
regions=('Iberia' 'Ireland' 'BeNeLux')
south_north_grids=(41 41 55)
west_east_grids=(52 46 46)
levels=(10 100)
# create a level loop
#for level in "${levels[@]}"; do
level=10
    for index in "${!regions[@]}"; do
        region="${regions[$index]}"
        south_north="${south_north_grids[$index]}"
        west_east="${west_east_grids[$index]}"

        # Loop over i and j indices to extract weibull parameters.
        # The catch is the number of processes that can be run in parallel are set to 98.
        count=0
        for ((i=0; i<$south_north; i++)); do
            for ((j=0; j<$west_east; j++)); do
                count=$((count+1))
                echo "Processing $region, $level, $i, $j"
                python "$root_dir/scripts/data_processing/Extract_wind_weibull_CERRA.py" "$region" "$level" "$i" "$j" &
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
            python "$root_dir/scripts/data_processing/Combine_weibull_CERRA.py" "$region" "$level" "$i" "0" "0" "$west_east" &
            count=$((count+1))
            if [ $count -eq 96 ]; then
                echo "Processing waits at $i"
                wait
                count=0
            fi
        done
        wait

        # Combine the weibull parameters along all directions and assign XLAT and XLONG coordinates.
        python "$root_dir/scripts/data_processing/Combine_weibull_CERRA.py" "$region" "$level" "0" "0" "$south_north" "0"

        # Remove the individual weibull files.
        rm -r "$root_dir/CERRA/$region/statistics_files/ws_$level/weibull"
    done
wait
echo "Script execution complete."