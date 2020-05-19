#!/bin/bash

if [ "$1" == "clear" ]
then
	for ex in Ex[0-9]
	do 
		cd $ex
		rm *.tse *.txt
		cd ..
	done

else
	for ex in Ex[0-9]
	do 
		cd $ex
		echo "Running ${ex}..."
		./*.sh > ${ex}_output.txt
		cd ..
	done
	echo "Done!"
fi
