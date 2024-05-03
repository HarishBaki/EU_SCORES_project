#!/bin/bash
#conda activate wrf-python_stable
k=16
start=1413
end=2265
log_file="log.txt"
echo "Looping from $start to $end with increments of $k:"
for i in $(seq "$start" "$k" "$end"); do
    for j in $(seq "$i" "$((i+k-1))"); do
        if [ "$j" -le "$end" ]; then
            echo "Number: $j"
            python Extracting_runwise_intermediate_files.py "$j" >> "$log_file" &
        fi
    done
    wait
done
echo "Script execution complete. Log saved to $log_file"

