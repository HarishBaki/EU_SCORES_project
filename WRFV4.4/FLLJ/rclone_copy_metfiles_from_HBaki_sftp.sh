case=$1
sim_start=$2
sim_end=$3
echo $sim_start
echo $sim_end
d=$sim_start
delta=
met_files=( )
while [ $(TZ=$TZ date -d "$d" +%s) -le $(TZ=$TZ date -d "$sim_end" +%s) ]
do
	year=$(date -d "$d" +%Y)
	month=$(date -d "$d" +%m)
	day=$(date -d "$d" +%d)
	hour=$(date -d "$d" +%H)
	met_files[${#met_files[*]}]="met_em.d01."$year"-"$month"-"$day"_"$hour":00:00.nc"
	d=$(TZ=$TZ date -d "$d + $delta hours" +%Y-%m-%d' '%H)
done
echo "Number of files are: "${#met_files[@]}

printf "%s\n" "${met_files[@]}" > metfiles.txt

rclone copy --progress --transfers 12 --files-from metfiles.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/New_runs/$case/WPS . 
