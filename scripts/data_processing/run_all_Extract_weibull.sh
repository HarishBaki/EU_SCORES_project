#conda activate wrf-python-stable
root_dir='/media/harish/SSD_4TB/EU_SCORES_project'
run='New_runs'
case='Germany_coast'
levels=(10) # 80 100 120 150)
I=($(seq 0 9))
J=($(seq 0 9))
for level in "${levels[@]}"; do
	mkdir -p $root_dir/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/variablewise_files/weibull_$level
	for i in "${I[@]}"; do
		for j in "${J[@]}"; do
			python $root_dir/scripts/data_processing/Extract_wind_weibull.py "$run" "$case" "$level" "$i" "$j" &
			echo "Processing for level: $level, i: $i, j: $j"
		done
	done
done
wait
echo "Script execution complete."
