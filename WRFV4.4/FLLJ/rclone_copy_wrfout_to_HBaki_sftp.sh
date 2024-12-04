Udrive_dir="$1"
case="$2"
run_dir="$3"
rclone copy --progress --transfers 12 . /tudelft.net/staff-umbrella/HBaki/$Udrive_dir/$run_dir --filter-from filter-file.txt
