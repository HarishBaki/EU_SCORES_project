#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
runs=('New_runs') # 'Validation_runs')
cases=('Netherlands_coast' 'Germany_coast' 'Portugal_coast' 'Ireland_coast')
cases=('Germany_coast' 'Portugal_coast' 'Ireland_coast')
levels=(80 100 120 150)
for run in "${runs[@]}"; do
	for case in "${cases[@]}"; do
		for level in "${levels[@]}"; do
			python $root_dir/scripts/data_processing/Extract_wind_power_density.py "$run" "$case" "$level"
		done
	done
done
echo "Script execution complete."
