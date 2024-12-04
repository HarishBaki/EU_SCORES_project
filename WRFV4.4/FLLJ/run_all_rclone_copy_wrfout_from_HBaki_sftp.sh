root_dir=$(pwd)
Udrive_dir="EU_SCORES_project/WRFV4.4/FLLJ"
cases=('FLLJ_1' 'FLLJ_2' 'FLLJ_3' 'FLLJ_4' 'FLLJ_5')
for ((i=3;i<${#cases[@]};++i)); do
	case=${cases[$i]}
	for run in $(seq 2 4); do
		run_dir=$case/WRF_run_$run
		bash rclone_copy_wrfout_from_HBaki_sftp.sh "$Udrive_dir" "$case" "$run_dir"
	done
done
