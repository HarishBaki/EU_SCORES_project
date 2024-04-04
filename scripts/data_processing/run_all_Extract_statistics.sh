#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
cases=('Germany_coast' 'Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
cases=('Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
 # create 21 dashboard ports
dashboard_ports=('8050' '8051' '8052' '8053' '8054' '8055' '8056' '8057' '8058' '8059' '8060' '8061' '8062' '8063' '8064' '8065' '8066' '8067' '8068' '8069' '8070')
# add a counter to keep track of the dashboard ports

# Loop over cases
for ((case_index=0; case_index<${#cases[@]}; case_index++)); do
    case="${cases[$case_index]}"
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files"
    dashboard_counter=0
    : '
    # === extracting wind statistics ===#
    file_names=('ws_10' 'ws_80' 'ws_100' 'ws_120' 'ws_150')
    file_names=('ws_10' 'ws_100')
    variable='ws'
    # Loop over file names
    for file_name in "${file_names[@]}"; do
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
        #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "8" &
        echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
        python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
        dashboard_counter=$((dashboard_counter+1))
    done
    wait
    '
    # === extracting wpd statistics ===#
    file_names=('wpd_80' 'wpd_100' 'wpd_120' 'wpd_150')
    file_names=('wpd_100')
    variable='wpd'

    # Loop over file names
    for file_name in "${file_names[@]}"; do
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
        #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "12" &
        echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
        python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
        dashboard_counter=$((dashboard_counter+1))
    done
    #wait
    
    : '
    # === extracting wind power statistics ===#
    capacity=('8MW' '15MW')
    file_names=('tp_80' 'tp_100' 'tp_120' 'tp_150')
    file_names=('tp_100')
    variable='power'
    
    # Loop over capacities
    for cap in "${capacity[@]}"; do
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$cap/$file_name"
            #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable"
            #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "12" &
            echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
            python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
            dashboard_counter=$((dashboard_counter+1))
        done
        #wait
    done
    #wait
    '
    # === extracting temperature statistics ===#
    file_name='T2'
    variable='T2'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &
    echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
    python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
    dashboard_counter=$((dashboard_counter+1))

    # === extracting SWDOWN2 statistics ===#
    file_name='SWDOWN2'
    variable='SWDOWN2'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &
    echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
    python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
    dashboard_counter=$((dashboard_counter+1))

    : '
    # === extracting temperature power statistics ===#
    file_name='spv'
    variable='PVO'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    #echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    #python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &
    echo "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}"
    python "$root_dir/scripts/data_processing/Rewrite_overall_statistics.py" "$run" "$case" "$file_name" "$variable" "8" "${dashboard_ports[$dashboard_counter]}" &
    dashboard_counter=$((dashboard_counter+1))
    '
    
    wait
    
done

echo "All statistics extracted successfully"