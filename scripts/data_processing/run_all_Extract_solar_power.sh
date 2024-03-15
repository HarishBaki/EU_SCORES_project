#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
case='Germany_coast'
python $root_dir/scripts/data_processing/Extract_solar_power.py "$run" "$case"
echo "Script execution complete."
