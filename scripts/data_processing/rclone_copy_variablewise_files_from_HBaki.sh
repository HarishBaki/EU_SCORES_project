run='New_runs'
cases=('Portugal_coast' 'Netherlands_coast' 'Ireland_coast')

exclude_files=('U10.nc' 'V10.nc' 'U_ZL_80.nc' 'U_ZL_100.nc' 'U_ZL_120.nc' 'U_ZL_150.nc' 'V_ZL_80.nc' 'V_ZL_100.nc' 'V_ZL_120.nc' 'V_ZL_150.nc')
exclude_args=""
for exclude_file in "${exclude_files[@]}"; do
    exclude_args+="--exclude $exclude_file "
done

for case in "${cases[@]}"; do
	rclone copy --progress --transfers 12 HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/variablewise_files $run/$case/Postprocessed/variablewise_files $exclude_args
done

run='Validation_runs'
cases=('Portugal_coast' 'Ireland_coast')

exclude_files=('U10.nc' 'V10.nc' 'U_ZL_80.nc' 'U_ZL_100.nc' 'U_ZL_120.nc' 'U_ZL_150.nc' 'V_ZL_80.nc' 'V_ZL_100.nc' 'V_ZL_120.nc' 'V_ZL_150.nc')
exclude_args=""
for exclude_file in "${exclude_files[@]}"; do
    exclude_args+="--exclude $exclude_file "
done

for case in "${cases[@]}"; do
	rclone copy --progress --transfers 12 HBaki_sftp:/tudelft.net/staff-umbrella/HBaki/WRFV4.4/EU_SCORES/$run/$case/Postprocessed/variablewise_files $run/$case/Postprocessed/variablewise_files $exclude_args
done