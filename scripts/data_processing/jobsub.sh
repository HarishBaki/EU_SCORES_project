#!/bin/bash
#SBATCH --job-name=python
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=4000

date
python Extract_statistics.py "New_runs" "Ireland_coast" "ws_100" "ws"
date