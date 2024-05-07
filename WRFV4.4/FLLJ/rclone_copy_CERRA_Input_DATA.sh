root_dir='/media/harish/SSD_4TB/EU_SCORES_project/WRFV4.4/FLLJ'
start_dates=('2016-02-21 12' '2016-03-03 12' '2016-02-08 18' '2017-01-09 06' '2017-01-29 12')
end_dates=('2016-02-22 18' '2016-03-04 18' '2016-02-10 00' '2017-01-10 12' '2017-01-30 18')
cases=('FLLJ_1' 'FLLJ_2' 'FLLJ_3' 'FLLJ_4' 'FLLJ_5')

for i in 2; do
    case=${cases[$i]}
    echo $case
    sim_start=${start_dates[$i]}
    sim_end=${end_dates[$i]}
    echo $sim_start $sim_end
    d=$sim_start
    delta=3
    met_files=( )

    d=$sim_start
    delta=3
    cerra_input_files=( )
    echo "$sim_start $sim_end $d $delta"
    while [ $(TZ=$TZ date -d "$d" +%s) -le $(TZ=$TZ date -d "$sim_end" +%s) ]
    do
        year=$(date -d "$d" +%Y)
        month=$(date -d "$d" +%m)
        day=$(date -d "$d" +%d)
        hour=$(date -d "$d" +%H)
        cerra_input_files[${#cerra_input_files[*]}]='/CERRA_'$year'_'$month'_'$day'-'$hour'_PRES.grb'
        cerra_input_files[${#cerra_input_files[*]}]='/CERRA_'$year'_'$month'_'$day'-'$hour'_SFC.grb'
        cerra_input_files[${#cerra_input_files[*]}]='/CERRA_'$year'_'$month'_'$day'-'$hour'_U10_V10.grb'
        cerra_input_files[${#cerra_input_files[*]}]='/ERA5_'$year'_'$month'_'$day'-'$hour'_soil.grb'
        d=$(TZ=$TZ date -d "$d + $delta hours" +%Y-%m-%d' '%H)
        echo $d
    done
    echo "Number of files are: "${#cerra_input_files[@]}

    printf "%s\n" "${cerra_input_files[@]}" > CERRA_Input_DATA.txt

    rclone copy --progress --transfers 12 --files-from CERRA_Input_DATA.txt /media/harish/External_2/CERRA/$year $case/Input_DATA/CERRA

done