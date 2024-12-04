root_dir=$(pwd)
Udrive_dir="EU_SCORES_project/WRFV4.4/FLLJ"
cases=('FLLJ_1' 'FLLJ_2' 'FLLJ_3' 'FLLJ_4' 'FLLJ_5')
for ((i=3;i<${#cases[@]};++i)); do
	case=${cases[$i]}
	for run in $(seq 2 4); do
		run_dir=$case/WRF_run_$run
		cd $run_dir
			echo $(pwd)
			cp $root_dir/rclone_copy_wrfout_to_HBaki_sftp.sh .
			cp $root_dir/filter-file.txt .
			bash rclone_copy_wrfout_to_HBaki_sftp.sh "$Udrive_dir" "$case" "$run_dir"
		cd $root_dir
	done
done
