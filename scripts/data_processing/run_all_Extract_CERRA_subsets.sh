#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'

var_dirs=('ws_10' 'ws_100' 't2m' 'swdown')
var_names=('ws' 'ws' 't2m' 'ssrd')

for index in "${!var_dirs[@]}"; do
    var_dir="${var_dirs[$index]}"
    var_name="${var_names[$index]}"
    echo "Processing $var_dir"
    python $root_dir/scripts/data_processing/Extract_CERRA_subsets.py "$var_dir" "$var_name" &
done
wait
echo "Script execution complete."

# Curate CERRA subsets, as follows.
# 1. Remove variable coordinate and dimension from all data
# 2. Convert T2M from K to C
# 3. Convert SWDOWN from J/m^2 to W/m^2
regions=('Iberia' 'Ireland' 'BeNeLux')
for index in "${!regions[@]}"; do
    region="${regions[$index]}"
    echo "Processing $region"
    python $root_dir/scripts/data_processing/curate_CERRA_variablewise.py "$region" &
done
wait
echo "Script execution complete."

# extracting wind power density
regions=('Iberia' 'Ireland' 'BeNeLux')
var_name=('ws')
level=100
for index in "${!regions[@]}"; do
    region="${regions[$index]}"
    echo "Processing $region"
    python $root_dir/scripts/data_processing/Extract_CERRA_wpd.py "$region" "$var_name" "$level" &
done
wait
echo "Script execution complete."

# extracting turbine power
regions=('Iberia' 'Ireland' 'BeNeLux')
var_name=('ws')
level=100
for index in "${!regions[@]}"; do
    region="${regions[$index]}"
    echo "Processing $region"
    turbine_types=('8MW' '15MW')
    for turbine_type in "${turbine_types[@]}"; do
        python $root_dir/scripts/data_processing/Extract_CERRA_turbine_power.py "$region" "$var_name" "$level" "$turbine_type" &
    done
done

# extracting solar power
regions=('Iberia' 'Ireland' 'BeNeLux')
for index in "${!regions[@]}"; do
    region="${regions[$index]}"
    echo "Processing $region"
    python $root_dir/scripts/data_processing/Extract_CERRA_solar_power.py "$region" &
done

wait
echo "Script execution complete."