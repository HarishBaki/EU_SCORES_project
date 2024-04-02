#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
regions=('Portugal' 'Ireland' 'BeNeLux')

# Loop over cases
for ((index=0; index<${#regions[@]}; index++)); do
    region="${regions[$index]}"
    
    file_names=('ws10' 'ws100' 'wpd_100' 't2m' 'swdown')
    variables=('ws' 'ws' 'wpd' 't2m' 'ssrd')
    # Loop over file names
    for ((file_index=0; file_index<${#file_names[@]}; file_index++)); do
        file_name="${file_names[$file_index]}"
        variable="${variables[$file_index]}"
        echo "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "8"
        python "$root_dir/scripts/data_processing/Extract_statistics_CERRA.py" "$region" "$file_name" "$variable" "8" &
    done
    wait    
done
wait
echo "All done"
