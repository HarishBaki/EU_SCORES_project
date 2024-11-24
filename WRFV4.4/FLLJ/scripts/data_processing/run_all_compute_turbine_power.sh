#!/bin/bash
# This script runs all the scripts needed to compute the turbine power
# for the WRF simulations.


# This loop extracts the POWER data from the MYNN simulations, which inherently compute the power from turbine models. 
for case in 1 2; do  # this loop is for the cases 1 and 2
    # This is loop for simulations with 3 hr CERRA data and 1 hr CERRA data
    for run in 1 2 5 8 9 12 16 17; do  # this loop is for the runs 1, 2, 5, 8, 9, 12, 16, 17
        run_dir="WRF_run_$run"
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
    done
done

for case in 3; do   # this loop is for the case 3
    for run in 2 5; do
        run_dir="WRF_run_$run"
        python extract_POWER.py $case $run $run_dir
        echo $case $run $run_dir
    done
done

# This loop computes the POWER data from the non-MYNN simulations. 
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
for case in 1 2; do 
    # This is loop for simulations with 3 hr CERRA data and 1 hr CERRA data
    for run in 3 4 6 7 10 11 13 14 15; do   # this loop is for the runs 3, 4, 6, 7, 15
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
wait

for case in 3; do   
    # This is loop for simulations with 3 hr CERRA data
    for run in 3 4; do  # this loop is for the runs 3, 4, 
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
wait

echo "All done"
