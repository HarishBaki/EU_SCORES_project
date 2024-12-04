cases=('FLLJ_1' 'FLLJ_2' 'FLLJ_3' 'FLLJ_4' 'FLLJ_5')
for ((i=3;i<${#cases[@]};++i)); do
	case=${cases[$i]}
	for run in $(seq 2 4); do
		run_dir=$case/WRF_run_$run
		echo $run_dir
		tail -1 $run_dir/rsl.out.0000
	done
done
