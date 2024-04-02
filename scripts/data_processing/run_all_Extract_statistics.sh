#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
cases=('Germany_coast' 'Ireland_coast' 'Portugal_coast' 'Netherlands_coast')
levels=(10 80 100 120 150)

# Loop over cases
for ((case_index=3; case_index<${#cases[@]}; case_index++)); do
    case="${cases[$case_index]}"
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files"
    : '
    # === extracting wind statistics ===#
    
    file_names=('ws_10' 'ws_80' 'ws_100' 'ws_120' 'ws_150')
    variable='ws'
    # chech if case_index is not 1
    if [ $case_index -ne 1 ]; then
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
            echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
            python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "8" &
        done
    fi
    wait

    # === extracting wpd statistics ===#
    file_names=('wpd_80' 'wpd_100' 'wpd_120' 'wpd_150')
    variable='wpd'

    # Loop over file names
    for file_name in "${file_names[@]}"; do
        mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
        echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
        python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "12" &
    done
    wait
    '
    # === extracting wind power statistics ===#
    capacity=('15MW')
    file_names=('tp_80' 'tp_100' 'tp_120' 'tp_150')
    variable='power'
    
    # Loop over capacities
    for cap in "${capacity[@]}"; do
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$cap/$file_name"
            echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable"
            python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$cap/$file_name" "$variable" "12" &
        done
        wait
    done
    wait

    # === extracting temperature statistics ===#
    file_name='T2'
    variable='T2'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &

    # === extracting SWDOWN2 statistics ===#
    file_name='SWDOWN2'
    variable='SWDOWN2'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &

    # === extracting temperature power statistics ===#
    file_name='spv'
    variable='PVO'
    mkdir -p "$root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/statistics_files/$file_name"
    echo "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable"
    python "$root_dir/scripts/data_processing/Extract_statistics.py" "$run" "$case" "$file_name" "$variable" "16" &
    wait
    
done
