case='Germany_coast'	#Change here for the region
i=2192				#Change here for run begin	
j=2265		#Change here for run end
while [ $i -le $j ] #Change this to make real.exe work
do
	DIR='WRF_'$i
	cd $DIR
		tail -1 rsl.out.0000
	cd ..
	echo 'Done '$DIR    
	((i++))
done
