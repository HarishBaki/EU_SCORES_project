#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
cases=('Netherlands_coast') # 'Germany_coast' 'Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
 # create 21 dashboard ports
dashboard_ports=('8050' '8051' '8052' '8053' '8054' '8055' '8056' '8057' '8058' '8059' '8060' '8061' '8062' '8063' '8064' '8065' '8066' '8067' '8068' '8069' '8070')
# add a counter to keep track of the dashboard ports
time_scales=('hour' 'month' 'season' 'year' 'overall')
statistics=('mean' 'std' 'quantile_5' 'quantile_95' 'quantile_99')
statistics=('quantile_95' 'quantile_99')
time_scale='season'
n_workers=24
# Semaphore to limit concurrent processes
MAX_CONCURRENT_JOBS=2
# Current number of running jobs
CURRENT_JOBS=0

# Function to wait until the number of running jobs is less than the maximum allowed
function wait_for_completion {
    while [ $CURRENT_JOBS -ge $MAX_CONCURRENT_JOBS ]; do
        sleep 1
        CURRENT_JOBS=$(jobs | wc -l)
    done
}
: '
# loop over statistics
for stat in "${statistics[@]}"; do
    # Loop over cases
    for ((case_index=0; case_index<${#cases[@]}; case_index++)); do
        case="${cases[$case_index]}"
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files"
        dashboard_counter=0
        
        # === extracting wind statistics ===#
        file_names=('ws_10' 'ws_80' 'ws_100' 'ws_120' 'ws_150')
        variable='ws'
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
            echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
            python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
            dashboard_counter=$((dashboard_counter+1))
            # Increment the current number of running jobs
            CURRENT_JOBS=$(jobs | wc -l)
        done
        
        # === extracting wpd statistics ===#
        file_names=('wpd_80' 'wpd_100' 'wpd_120' 'wpd_150')
        variable='wpd'

        # Loop over file names
        for file_name in "${file_names[@]}"; do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
            echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
            python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
            dashboard_counter=$((dashboard_counter+1))
            # Increment the current number of running jobs
            CURRENT_JOBS=$(jobs | wc -l)
        done
        
        # === extracting wind power statistics ===#
        capacity=('8MW' '15MW')
        file_names=('tp_80' 'tp_100' 'tp_120' 'tp_150')
        variable='power'
        
        # Loop over capacities
        for cap in "${capacity[@]}"; do
            # Loop over file names
            for file_name in "${file_names[@]}"; do
                # Wait until the number of running jobs is less than the maximum allowed
                wait_for_completion
                mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$cap/$file_name"
                echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
                python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
                dashboard_counter=$((dashboard_counter+1))
                # Increment the current number of running jobs
                CURRENT_JOBS=$(jobs | wc -l)
            done
        done
        
        # === extracting temperature statistics ===#
        file_name='T2'
        variable='T2'
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
        python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
        dashboard_counter=$((dashboard_counter+1))
        # Increment the current number of running jobs
        CURRENT_JOBS=$(jobs | wc -l)

        # === extracting SWDOWN2 statistics ===#
        file_name='SWDOWN2'
        variable='SWDOWN2'
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
        python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
        dashboard_counter=$((dashboard_counter+1))
        # Increment the current number of running jobs
        CURRENT_JOBS=$(jobs | wc -l)
        
        # === extracting temperature power statistics ===#
        file_name='spv'
        variable='PVO'
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale"
        python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$stat" "$time_scale" &
        dashboard_counter=$((dashboard_counter+1))
        # Increment the current number of running jobs
        CURRENT_JOBS=$(jobs | wc -l)
        
    done
done
'

wait

# Once all the jobs are done, we have to compute the coefficient of variance
cases=('Germany_coast' 'Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
# Semaphore to limit concurrent processes
MAX_CONCURRENT_JOBS=8
# Current number of running jobs
CURRENT_JOBS=0

# Loop over cases
for ((case_index=0; case_index<${#cases[@]}; case_index++)); do
    case="${cases[$case_index]}"
    # === extracting wind statistics ===#
    file_names=('ws_10' 'ws_80' 'ws_100' 'ws_120' 'ws_150')
    variable='ws'
    # Loop over file names
    for file_name in "${file_names[@]}"; do
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable"
        python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable" &
        CURRENT_JOBS=$(jobs | wc -l)
    done

    # === extracting wpd statistics ===#
    file_names=('wpd_80' 'wpd_100' 'wpd_120' 'wpd_150')
    variable='wpd'

    # Loop over file names
    for file_name in "${file_names[@]}"; do
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable"
        python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable" &
        # Increment the current number of running jobs
        CURRENT_JOBS=$(jobs | wc -l)
    done

    # === extracting wind power statistics ===#
    capacity=('8MW' '15MW')
    file_names=('tp_80' 'tp_100' 'tp_120' 'tp_150')
    variable='power'
    
    # Loop over capacities
    for cap in "${capacity[@]}"; do
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$cap/$file_name"
            echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$cap/$file_name" "$variable"
            python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$cap/$file_name" "$variable" &
            # Increment the current number of running jobs
            CURRENT_JOBS=$(jobs | wc -l)
        done
    done
    
    # === extracting temperature statistics ===#
    file_name='T2'
    variable='T2'
    # Wait until the number of running jobs is less than the maximum allowed
    wait_for_completion
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable" &
    dashboard_counter=$((dashboard_counter+1))
    # Increment the current number of running jobs
    CURRENT_JOBS=$(jobs | wc -l)

    # === extracting SWDOWN2 statistics ===#
    file_name='SWDOWN2'
    variable='SWDOWN2'
    # Wait until the number of running jobs is less than the maximum allowed
    wait_for_completion
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable" &
    dashboard_counter=$((dashboard_counter+1))
    # Increment the current number of running jobs
    CURRENT_JOBS=$(jobs | wc -l)
    
    # === extracting temperature power statistics ===#
    file_name='spv'
    variable='PVO'
    # Wait until the number of running jobs is less than the maximum allowed
    wait_for_completion
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_CoV.py" "$run" "$case" "$file_name" "$variable" &
    dashboard_counter=$((dashboard_counter+1))
    # Increment the current number of running jobs
    CURRENT_JOBS=$(jobs | wc -l)
done
wait
echo "All statistics extracted successfully"