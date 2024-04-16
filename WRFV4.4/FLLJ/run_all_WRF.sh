root_dir=$(pwd)
Udrive_dir="EU_SCORES_project/WRFV4.4/FLLJ"
start_dates=('2016-02-21 12' '2016-03-03 12')
end_dates=('2016-02-22 18' '2016-03-04 18')
cases=('FLLJ_1' 'FLLJ_2')
i=0
case=${cases[$i]}
start_date=${start_dates[$i]}
end_date=${end_dates[$i]}

start_year=$(date -ud "$start_date" +"%Y")
start_month=$(date -ud "$start_date" +"%m")
start_day=$(date -ud "$start_date" +"%d")
start_hour=$(date -ud "$start_date" +"%H")
end_year=$(date -ud "$end_date" +"%Y")
end_month=$(date -ud "$end_date" +"%m")
end_day=$(date -ud "$end_date" +"%d")
end_hour=$(date -ud "$end_date" +"%H")

# call WRF pipeline here
run=1
run_dir=$case/WRF_run_$run

echo $root_dir $Udrive_dir $case $run_dir

mkdir -p $run_dir
cd $run_dir
	# copy metfiles
	metgrid_dir="$Udrive_dir/$case/WPS_run_$run"
	rclone copy --progress --transfers 12 /tudelft.net/staff-umbrella/HBaki/$metgrid_dir/metfiles metfiles
	ln -sf metfiles/* .
	
	cp -r $WRF_DIR/run/* .
	rm *.exe
	rm namelist.input
	ln -sf $WRF_DIR/main/*.exe .
	
	cp $root_dir"/namelists/run_$run"* namelist.input
	sed -i -e "s/ start_year = / start_year = $start_year,$start_year,$start_year,/g" namelist.input
	sed -i -e "s/ start_month = / start_month = $start_month,$start_month,$start_month,/g" namelist.input
	sed -i -e "s/ start_day = / start_day = $start_day,$start_day,$start_day,/g" namelist.input
	sed -i -e "s/ start_hour = / start_hour = $start_hour,$start_hour,$start_hour,/g" namelist.input
	sed -i -e "s/ end_year = / end_year = $end_year,$end_year,$end_year,/g" namelist.input
	sed -i -e "s/ end_month = / end_month = $end_month,$end_month,$end_month,/g" namelist.input
	sed -i -e "s/ end_day = / end_day = $end_day,$end_day,$end_day,/g" namelist.input
	sed -i -e "s/ end_hour = / end_hour = $end_hour,$end_hour,$end_hour,/g" namelist.input	
	
	cp $root_dir/wind-turbine-* .
	cp $root_dir/windturbines.txt .
	cp $root_dir/tslist .
	cp $root_dir/myoutfields.txt .
    
    cp $root_dir/rclone_copy_wrfout_to_HBaki_sftp.sh .
    cp $root_dir/filter-file.txt .
    
    cp $root_dir/submit_real_wrf_backup.sh .
    sed -i -e "s/\#SBATCH --job-name=\"case_name\"/\#SBATCH --job-name=\"WRF_$run\"/g" submit_real_wrf_backup.sh
    sbatch submit_real_wrf_backup.sh "$Udrive_dir" "$case" "$run_dir"
cd $root_dir
