#!/bin/bash
#conda activate wrf-python_stable
k=8
start=27
end=261
locations=('LOT1' 'LOT2')
log_file="log_tslist.txt"
echo "Looping from $start to $end with increments of $k:"
for i in $(seq "$start" "$k" "$end"); do
    for j in $(seq "$i" "$((i+k-1))"); do
        if [ "$j" -le "$end" ]; then
            
            for loc in "${locations[@]}"; do
            	echo "Number: $j, location: $loc"
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "TS" >> "$log_file" &
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "UU" >> "$log_file" &
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "VV" >> "$log_file" &
            done
        fi
    done
    wait
done
echo "Script execution complete. Log saved to $log_file"

k=2
start=262
end=2265
locations=('LOT1' 'LOT2' '6308' '6313' '6400' '6407' '6418' '7010')
log_file="log_tslist.txt"
echo "Looping from $start to $end with increments of $k:"
for i in $(seq "$start" "$k" "$end"); do
    for j in $(seq "$i" "$((i+k-1))"); do
        if [ "$j" -le "$end" ]; then
            
            for loc in "${locations[@]}"; do
            	echo "Number: $j, location: $loc"
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "TS" >> "$log_file" &
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "UU" >> "$log_file" &
                python Extracting_runwise_intermediate_tslist_files.py "$j" "$loc" "VV" >> "$log_file" &
            done
        fi
    done
    wait
done
echo "Script execution complete. Log saved to $log_file"
