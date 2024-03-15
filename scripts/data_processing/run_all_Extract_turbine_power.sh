#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
runs=('New_runs') # 'Validation_runs')
cases=('Germany_coast') #'Portugal_coast' 'Ireland_coast' 'Netherlands_coast')
levels=(80 100 120 150)
turbine_types=('8MW' '15MW')
for run in "${runs[@]}"; do
	for case in "${cases[@]}"; do
		for level in "${levels[@]}"; do
			for turbine_type in "${turbine_types[@]}"; do
				python $root_dir/scripts/data_processing/Extract_turbine_power.py "$run" "$case" "$level" "$turbine_type"
			done
		done
	done
done
echo "Script execution complete."
