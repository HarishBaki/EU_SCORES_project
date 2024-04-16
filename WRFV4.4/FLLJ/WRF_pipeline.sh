root_dir="$1"
WRF_source_dir="$2"
metgrid_dir="$3"
start_date="$4"
end_date="$5"
run_dir="$6"
namelist_input="$7"
run="$8"

start_year=$(date -ud "$start_date" +"%Y")
start_month=$(date -ud "$start_date" +"%m")
start_day=$(date -ud "$start_date" +"%d")
start_hour=$(date -ud "$start_date" +"%H")
end_year=$(date -ud "$end_date" +"%Y")
end_month=$(date -ud "$end_date" +"%m")
end_day=$(date -ud "$end_date" +"%d")
end_hour=$(date -ud "$end_date" +"%H")

echo $start_year $start_month $start_day $start_hour $end_year $end_month $end_day $end_hour

cp -r $WRF_source_dir/run/* .
rm *.exe
rm namelist.input
ln -sf $WRF_source_dir/main/*.exe .
ln -sf $metgrid_dir/met_em.d0* . #Change this accordingly
cp $root_dir/wind-turbine-* .
cp $root_dir/windturbines.txt .
cp $root_dir/tslist .
cp $root_dir/myoutfields.txt .

cp $namelist_input namelist.input
sed -i -e "s/ start_year = / start_year = $start_year,$start_year,$start_year,/g" namelist.input
sed -i -e "s/ start_month = / start_month = $start_month,$start_month,$start_month,/g" namelist.input
sed -i -e "s/ start_day = / start_day = $start_day,$start_day,$start_day,/g" namelist.input
sed -i -e "s/ start_hour = / start_hour = $start_hour,$start_hour,$start_hour,/g" namelist.input
sed -i -e "s/ end_year = / end_year = $end_year,$end_year,$end_year,/g" namelist.input
sed -i -e "s/ end_month = / end_month = $end_month,$end_month,$end_month,/g" namelist.input
sed -i -e "s/ end_day = / end_day = $end_day,$end_day,$end_day,/g" namelist.input
sed -i -e "s/ end_hour = / end_hour = $end_hour,$end_hour,$end_hour,/g" namelist.input

cp $root_dir/submit_real_wrf_backup.sh .
#sed -i -e "s/\#SBATCH --job-name=\"case_name\"/\#SBATCH --job-name=\"$WRF\_$run\"/g" submit_real_wrf_backup.sh
sbatch submit_real_wrf_backup.sh
