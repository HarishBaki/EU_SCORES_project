#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
cases=('Germany_coast') # 'Portugal_coast' 'Ireland_coast' 'Netherlands_coast')
levels=(80) #100 120 150)
south_north_grids=(63 127 127 199)
west_east_grids=(63 127 127 199)
# Loop over cases
for ((case_index=0; case_index<${#cases[@]}; case_index++)); do
    case="${cases[$case_index]}"
    south_north="${south_north_grids[$case_index]}"
    west_east="${west_east_grids[$case_index]}"
    
    # Loop over levels
    for level in "${levels[@]}"; do
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/variablewise_files/weibull_$level"
        # Loop over i and j indices
        for ((i=0; i<$south_north; i++)); do
            for ((j=0; j<$west_east; j++)); do
                python "$root_dir/scripts/data_processing/Extract_wind_weibull.py" "$run" "$case" "$level" "$i" "$j" &
                echo "Processing $case, $level, $i, $j"
            done
            wait
        done
    done
done

echo "Script execution complete."
