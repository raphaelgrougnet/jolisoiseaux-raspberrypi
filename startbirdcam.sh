#!/bin/bash
counter=0

echo -e "\n\n\nBACKYARD BIRDCAM - RDW 2022\n"
echo -e "\n$(date)\n\nStarting Bird Detection now ... \n"

while true ; do

	# start python object detection program
	python3 /home/pi/Desktop/Object_Detection_Files/birdcam.py
	if [[ "$?" -eq 1 ]]
        then
                exit # Exit program because [Ctrl-C] exit pressed while in python script
        else
	# disable Ctrl-C while in this loop
	trap "" SIGINT SIGABRT
        # start hires photo burst
	let "counter++"  # logs number of photo bursts that have been taken
        echo -e "\nBird detected!! $(date) - Taking hires camera photo burst series number $counter"
	# set save location of camera burst photos
        cd /home/pi/Desktop/Object_Detection_Files/HiRes
	# take camera burst series
	sudo raspistill -ex sports -bm -n -o HiRes_$(date +"%Y-%m-%d_%H-%M-%S.%3N_")%02d.jpg -t 10000 -tl 0 -th 0:0:0 --thumb none
        # increase or decrease '-t 10000' to change number of photos in the burst
        echo -e "\nReturning to Object Detection Mode\n"
        # re-enable [Ctrl-C] key
        trap - SIGINT SIGABRT
	fi
done
