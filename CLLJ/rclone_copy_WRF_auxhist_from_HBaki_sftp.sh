runs='Validation_runs'
case='Portugal_coast'

sim_start=''

aux_files=( )
for wrf in $(seq 1571 1 1578); do
    DIR=${runs}/${case}/WRF_${wrf}
        rclone copy --progress --transfers 1 HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/${case}/wrf${wrf}/auxhist${auxhist} ${runs}/${case}/wrf${wrf}/auxhist${auxhist}
${runs}/${case}/wrf${wrf}/auxhist${auxhist} ${runs}/${case}/wrf${wrf}/auxhist${auxhist}
    done
done
