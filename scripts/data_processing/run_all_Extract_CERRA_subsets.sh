#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'

var_dirs=('ws10' 'ws100' 't2m' 'swdown')
var_names=('ws' 'ws' 't2m' 'ssrd')

for index in "${!var_dirs[@]}"; do
    var_dir="${var_dirs[$index]}"
    var_name="${var_names[$index]}"
    echo "Processing $var_dir"
    python $root_dir/scripts/data_processing/Extract_CERRA_subsets.py "$var_dir" "$var_name" &
done
wait
echo "Script execution complete."

# extracting wind power density
regions=('Portugal' 'Ireland' 'BeNeLux')
var_name=('ws')
level=100
for index in "${!regions[@]}"; do
    region="${regions[$index]}"
    echo "Processing $region"
    python $root_dir/scripts/data_processing/Extract_CERRA_wpd.py "$region" "$var_name" "$level" &
done
wait
echo "Script execution complete."