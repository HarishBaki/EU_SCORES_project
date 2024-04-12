#!/bin/bash
#conda activate wrf-python-stable
for year in $(seq 2018 1 2018)
do
	start_date="$year-01-01 00"
	end_date="$year-12-31 23"
	d_d=$start_date
	d_h=$d_d
	delta_d=1
	delta_h=3
	TZ=UTC
	main_dir=$(pwd)
	while [ $(date -d "$d_d" +%s) -le $(date -d "$end_date" +%s) ]
	do
		echo "d_d "$d_d
		d_d=$(TZ=$TZ date -d "$d_d + $delta_d days" +%Y-%m-%d' '%H)
		#while [ $(date -d "$d_h" +%s) -lt $(date -d "$d_d" +%s) ]
		while [ $(date -d "$d_h" +%s) -lt $(date -d "$d_d" +%s) ] && [ $(date -d "$d_h" +%s) -lt $(date -d "$end_date" +%s) ]
		do
			x_year=$(date -d "$d_h" +%Y)
			x_month=$(date -d "$d_h" +%m)
			x_day=$(date -d "$d_h" +%d)
			x_time=$(date -d "$d_h" +%H)
			echo "d_h "$d_h", $x_year, $x_month, $x_day, $x_time"
			mkdir $x_year
			cd $x_year
				if ls "CERRA_"$x_year"_"$x_month"_"$x_day"-"$x_time"_PRES.grb" \
				&& ls "CERRA_"$x_year"_"$x_month"_"$x_day"-"$x_time"_SFC.grb" \
				&& ls "ERA5_"$x_year"_"$x_month"_"$x_day"-"$x_time"_soil.grb" 1>/dev/null 2>&1;
				then
					x_files=($(ls "CERRA_"$x_year"_"$x_month"_"$x_day"-"$x_time"_PRES.grb" "CERRA_"$x_year"_"$x_month"_"$x_day"-"$x_time"_SFC.grb" "ERA5_"$x_year"_"$x_month"_"$x_day"-"$x_time"_soil.grb"))
					echo "All files exist:"$(ls -l ${x_files[*]})
				else
					echo "One or more files are missing" 
					python $main_dir/CERRA_convert_ERA5.py '/home/harish/.cdsapirc' $x_year $x_month $x_day $x_time
				fi
			cd $main_dir
			d_h=$(TZ=$TZ date -d "$d_h + $delta_h hours" +%Y-%m-%d' '%H)
		done
	done
	echo "Done "$year
done
