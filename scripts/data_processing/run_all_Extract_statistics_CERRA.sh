#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
regions=('Iberia' 'Ireland' 'BeNeLux')

# Loop over cases
for ((index=0; index<${#regions[@]}; index++)); do
    region="${regions[$index]}"
    
    file_names=('ws_10' 'ws_100' 'wpd_100' 't2m' 'swdown' 'spv')
    variables=('ws' 'ws' 'wpd' 't2m' 'ssrd' 'PVO')
    # Loop over file names
    for ((file_index=0; file_index<${#file_names[@]}; file_index++)); do
        file_name="${file_names[$file_index]}"
        variable="${variables[$file_index]}"
        echo "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "4"
        python "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "4" &
    done

    capacity=('8MW' '15MW')
    file_names=('tp_100')
    variable='power'
    # Loop over capacities
    for cap in "${capacity[@]}"; do
        # Loop over file names
        for file_name in "${file_names[@]}"; do
            echo "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$cap/$file_name" "$variable" "4"
            python "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$cap/$file_name" "$variable" "4" &
        done
    done
    wait    
done
wait
echo "All done"
