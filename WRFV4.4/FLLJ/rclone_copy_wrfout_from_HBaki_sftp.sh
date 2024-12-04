Udrive_dir="$1"
case="$2"
run_dir="$3"
rclone copy --progress --transfers 12 HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/$Udrive_dir/$run_dir $run_dir
