#conda activate wrf-python-stable
# Semaphore to limit concurrent processes
MAX_CONCURRENT_JOBS=8
# Current number of running jobs
CURRENT_JOBS=0

# Function to wait until the number of running jobs is less than the maximum allowed
function wait_for_completion {
    while [ $CURRENT_JOBS -ge $MAX_CONCURRENT_JOBS ]; do
        sleep 1
        CURRENT_JOBS=$(jobs | wc -l)
    done
}
n_workers=4
# Dashboard ports
# create random ports based on the max_concurrent_jobs
dashboard_ports=($(shuf -i 8000-9000 -n $MAX_CONCURRENT_JOBS))
dashboard_counter=0

root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
regions=('Iberia' 'Ireland' 'BeNeLux')
statistics=('mean' 'std' 'quantile_5' 'quantile_95' 'quantile_99')
time_scales=('season')   # ('hour' 'month' 'season' 'year' 'overall')  

# Loop over cases
for ((index=0; index<${#regions[@]}; index++)); do
    region="${regions[$index]}"
    file_names=('ws_10' 'ws_100' 'wpd_100' 't2m' 'swdown' 'spv' '8MW/tp_100' '15MW/tp_100')
    variables=('ws' 'ws' 'wpd' 't2m' 'ssrd' 'PVO' 'power' 'power')
    # Loop over file names
    for ((file_index=0; file_index<${#file_names[@]}; file_index++)); do
        file_name="${file_names[$file_index]}"
        variable="${variables[$file_index]}"
        # Loop over statistics
        for ((stat_index=0; stat_index<${#statistics[@]}; stat_index++)); do
            statistic="${statistics[$stat_index]}"
            # Loop over time scales
            for ((time_index=0; time_index<${#time_scales[@]}; time_index++)); do
                time_scale="${time_scales[$time_index]}"
                # Wait until the number of running jobs is less than the maximum allowed
                wait_for_completion
                echo "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$statistic" "$time_scale"
                python "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "$n_workers" "${dashboard_ports[$dashboard_counter]}" "$statistic" "$time_scale" &
                dashboard_counter=$((dashboard_counter+1))
                # If the dashboard counter is equal to the maximum number of concurrent jobs, reset it to 0
                if [ $dashboard_counter -eq $MAX_CONCURRENT_JOBS ]; then
                    dashboard_counter=0
                fi
                # Increment the current number of running jobs
                CURRENT_JOBS=$(jobs | wc -l)
            done
        done
    done   
done
wait
echo "All done"
