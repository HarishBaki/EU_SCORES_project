#!/bin/bash
# This script runs all the scripts needed to compute the turbine power
# for the WRF simulations.
: '
for case in 1 2
do
    for run in 1 2 5 8
    do
        python extract_POWER.py $case $run
        echo $case $run
    done
done
'

# Semaphore to limit concurrent processes
MAX_CONCURRENT_JOBS=48
# Current number of running jobs
CURRENT_JOBS=0
# Function to wait until the number of running jobs is less than the maximum allowed
function wait_for_completion {
    while [ $CURRENT_JOBS -ge $MAX_CONCURRENT_JOBS ]; do
        sleep 1
        CURRENT_JOBS=$(jobs | wc -l)
    done
}

# number_of_turbines are 182
case=2
for run in 3 4 6 7
do
    for j in $(seq 0 181)
    do
        # Wait until the number of running jobs is less than the maximum allowed
        wait_for_completion
        python compute_turbine_power.py $case $run $j "False" &
        CURRENT_JOBS=$(jobs | wc -l)
        echo $case $run $j
    done
    wait
    # Combine the weibull parameters along individual south_north direciton and all west_east direction.
    python compute_turbine_power.py $case $run 0 "True" 
    echo $case $run
    wait
done
wait
echo "All done"
