run=$1
case=$2
DIR=$3
rclone copy --progress --transfers 2 --filter-from filter-file.txt HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/EU_SCORES_project/WRFV4.4/EU_SCORES/$run/$case/$DIR $run/$case/$DIR