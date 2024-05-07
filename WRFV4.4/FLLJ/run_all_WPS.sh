WPS_source_dir=/media/sukanta/HD2/WRF/WRFV4.4/WPS # this is the WPS installation directory

root_dir='/media/harish/SSD_4TB/EU_SCORES_project/WRFV4.4/FLLJ'
start_dates=('2016-02-21_12:00:00' '2016-03-03_12:00:00' '2016-02-08_18:00:00' '2017-01-09_06:00:00' '2017-01-29_12:00:00')
end_dates=('2016-02-22_18:00:00' '2016-03-04_18:00:00' '2016-02-10_00:00:00' '2017-01-10_12:00:00' '2017-01-30_18:00:00')
cases=('FLLJ_1' 'FLLJ_2' 'FLLJ_3' 'FLLJ_4' 'FLLJ_5')
#for (( i=3; i<${#cases[@]}; i++ ));
for i in 2;
do
    case=${cases[$i]}
    echo $case
    # there are folders in the WPS directory, which are ends with _geogrid. read them
    runs=('run_5' 'run_7')     # actual runs ('run_1' 'run_2,3,4' 'run_5' 'run_6' 'run_7' 'run_8')
    # loop over the geogrid_dirs
    for run in ${runs[@]};
    do
    	geogrid_dir=$root_dir/$run"_geogrid"
        # from the geogrid_dir, exclude the _geogrid part, and extract the WPS directory name
        # only read the last part of the path, which is the directory name
        WPS_dir="WPS_"$run
        # create the WPS run directory
        run_dir=$root_dir/$case/$WPS_dir
        mkdir -p $run_dir
        cd $run_dir
            # Call the WPS pipeline here
            if [ $run == 'run_1' ]; then
                grib_prefix='ERA5'
                grib_source_dir=$root_dir/$case/Input_DATA/ERA5
                Vtable='Vtable.ERA-interim.pl'
                bash $root_dir/WPS_pipeline.sh $root_dir $WPS_source_dir $geogrid_dir ${start_dates[$i]} ${end_dates[$i]} $grib_source_dir $grib_prefix $Vtable &
            elif [ $run == 'run_8' ]; then
                grib_prefix='gfs'
                grib_source_dir=$root_dir/$case/Input_DATA/GFS_forecast
                Vtable='Vtable.GFS'
                bash $root_dir/WPS_pipeline.sh $root_dir $WPS_source_dir $geogrid_dir ${start_dates[$i]} ${end_dates[$i]} $grib_source_dir $grib_prefix $Vtable &
            else
                grib_prefix='CERRA'
                grib_source_dir=$root_dir/$case/Input_DATA/CERRA
                Vtable=''
                bash $root_dir/WPS_pipeline.sh $root_dir $WPS_source_dir $geogrid_dir ${start_dates[$i]} ${end_dates[$i]} $grib_source_dir $grib_prefix $Vtable &
            fi
            echo $root_dir $WPS_source_dir $geogrid_dir ${start_dates[$i]} ${end_dates[$i]} $grib_source_dir $grib_prefix $Vtable
        cd $root_dir
    done
    wait
done
wait
echo "WPS pipeline completed" 
