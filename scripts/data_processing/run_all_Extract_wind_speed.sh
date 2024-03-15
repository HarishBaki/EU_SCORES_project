#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
case='Germany_coast'
levels=(10 80 100 120 150)
for level in "${levels[@]}"; do
	python $root_dir/scripts/data_processing/Extract_wind_speed.py "$run" "$case" "$level"
done
echo "Script execution complete."
