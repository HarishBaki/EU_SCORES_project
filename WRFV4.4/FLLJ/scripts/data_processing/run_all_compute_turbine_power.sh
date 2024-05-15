#!/bin/bash
# This script runs all the scripts needed to compute the turbine power
# for the WRF simulations.
: '
for case in 1 2
do
    for run in 8; do
        run_dir="WRF_run_$run"
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
    done

    for run in 2 5
    do
        run_dir="WRF_run_$run"
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
        run_dir="WRF_run_"$((run + 7))
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
    done

done

for case in 3
do
    for run in 5; do
        run_dir="WRF_run_$run"
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
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
for case in 1 2
do
    for run in 15 #3 4 6 7
    do
        run_dir="WRF_run_$run"
        for j in $(seq 0 181)
        do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            python compute_turbine_power.py $case $run $run_dir $j "False" &
            CURRENT_JOBS=$(jobs | wc -l)
            echo $case $run $j
        done
        wait
        # Combine the weibull parameters along individual south_north direciton and all west_east direction.
        python compute_turbine_power.py $case $run $run_dir 0 "True" 
        echo $case $run
        wait
        : '
        run_dir="WRF_run_"$((run + 7))
        for j in $(seq 0 181)
        do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            python compute_turbine_power.py $case $run $run_dir $j "False" &
            CURRENT_JOBS=$(jobs | wc -l)
            echo $case $run $j
        done
        wait
        # Combine the weibull parameters along individual south_north direciton and all west_east direction.
        python compute_turbine_power.py $case $run $run_dir 0 "True" 
        echo $case $run
        wait
        '
    done
    wait
done
: '
for case in 3
do
    for run in 7
    do
        run_dir="WRF_run_$run"
        for j in $(seq 0 181)
        do
            # Wait until the number of running jobs is less than the maximum allowed
            wait_for_completion
            python compute_turbine_power.py $case $run $run_dir $j "False" &
            CURRENT_JOBS=$(jobs | wc -l)
            echo $case $run $j
        done
        wait
        # Combine the weibull parameters along individual south_north direciton and all west_east direction.
        python compute_turbine_power.py $case $run $run_dir 0 "True" 
        echo $case $run
        wait
    done
    wait
done
'
wait

echo "All done"
