case='Portugal_coast'
for run in 'New_runs'; do
    for run_id in $(seq 1 1 12); do
        DIR=WRF_$run_id
        bash rclone_copy_WRF_from_HBaki.sh $run $case $DIR &
    done
done
wait
echo "Done copying"
