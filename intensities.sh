#!/bin/sh

# $Header$

DIRECTORY=$1
# Actually, the directory is going to be passed to /bin/date for interpolation
# as if it were GMT.

if [ "x$DIRECTORY" = "x" ]
then
    echo "Usage: $0 <directory>"
    exit 1
fi



if [ -t 0 ]
then
    TTY=$(tty)
else
    TTY=/dev/null
fi

case $(dirname $0) in
  /*) BASEDIR=$(dirname $0) ;;
  *) BASEDIR=$(pwd)/$(dirname $0) ;;
esac


cd $DIRECTORY
OLDDIR=$(pwd)
rm -f known-cameras.dxt
touch known-cameras.dxt

# An obvious optimisation -- check to see if the .dat file is newer than
# every image.

export TZ=GMT
find $(date +$DIRECTORY) -type d -print | ( while read directory
    do
	cd $OLDDIR
	cd $directory
	#echo "cd $directory"

	if [ "$(echo *-[0-9][0-9]:[0-9][0-9].jpg)" = "*-[0-9][0-9]:[0-9][0-9].jpg" ]
	then
	    # no appropriate images here
	    echo "No images in $directory (there might be subdirectories, though)." > $TTY
	    continue
	fi
	    

	CAMERAS=$(echo *-[0-9][0-9]:[0-9][0-9].jpg | sed 's/-[0-9][0-9]:[0-9][0-9].jpg//g' | tr ' ' '\n' | sort | uniq)

	echo "Cameras are: $(echo $CAMERAS | tr '\n' ' ')" > $TTY
	for CAMERA in $CAMERAS
	do
	    if grep -q "^$CAMERA\$" $OLDDIR/known-cameras.dxt
	    then
		echo "Already seen this camera" > /dev/null
	    else
		echo $CAMERA >> $OLDDIR/known-cameras.dxt
	    fi
	    IMAGES=$(echo ${CAMERA}-[0-9][0-9]:[0-9][0-9].jpg)
	    NEEDS_REBUILD=0
	    for IMAGE in $IMAGES
	    do
		if [ $IMAGE -nt ${CAMERA}.dat ]
		then
		    NEEDS_REBUILD=1
		    break
		fi
	    done

	    if [ $NEEDS_REBUILD = 1 ]
	    then
		echo -n "Doing $CAMERA in $directory  " > $TTY
		rm -f ${CAMERA}.dat
		echo "# $(pwd)/${CAMERA}-*.jpg" >> ${CAMERA}.dat
		for IMAGE in $IMAGES
		do
		    SHORT=$(echo $IMAGE | sed -e "s/${CAMERA}-//" -e 's/.jpg$//')
		    if identify ${IMAGE} 2>&1 | grep -q -e 'Corrupt JPEG' -e 'Premature end of JPEG file'
		    then
			echo -n "\rrm'ing $CAMERA $SHORT (corrupt) in $directory" > $TTY
			rm ${IMAGE}
		    else
			echo -n "\rDoing $CAMERA $SHORT in $directory          " > $TTY
			(
			    ls -lT ${IMAGE} |  awk '{print $9 "-" $6 "-" $7 "@" $8 }'
			    identify -verbose ${IMAGE} | grep -e '^      Mean:' -e '^      Standard deviation:' |  sed 's/^.*(//' | sed 's/).*$//'
			)  |  tr '\n' ' ' >> ${CAMERA}.dat
			echo >> ${CAMERA}.dat
		    fi
		done
		echo "\r$CAMERA in $directory data done                               " > $TTY
	    else
		echo "Skipping recalc of $CAMERA in $directory" > $TTY
	    fi


	    if [ ${CAMERA}.dat -nt ${CAMERA}.gnuplot ]
	    then
		rm -f ${CAMERA}.gnuplot
		echo "set output \"${CAMERA}.png\"" >> ${CAMERA}.gnuplot
		echo 'set timefmt "%Y-%b-%d@%H:%M:%S"' >> ${CAMERA}.gnuplot
		echo "set xdata time"  >> ${CAMERA}.gnuplot
		echo "set term png" >> ${CAMERA}.gnuplot
		echo "plot \"${CAMERA}.dat\" using 1:2:3 with yerrorlines title \"Red\", \"${CAMERA}.dat\" using 1:4:5 with yerrorlines title \"Green\", \"${CAMERA}.dat\" using 1:6:7 with yerrorlines title \"Blue\"" >> ${CAMERA}.gnuplot
		
		echo "set output \"${CAMERA}+spread.png\""  >> ${CAMERA}.gnuplot
		echo "set xdata"  >> ${CAMERA}.gnuplot
		echo "plot \"${CAMERA}.dat\" using 2:3 title \"Red\", \"${CAMERA}.dat\" using 4:5 title \"Green\", \"${CAMERA}.dat\" using 6:7 title \"Blue\"" >> ${CAMERA}.gnuplot
		
		echo "set output \"${CAMERA}+ratio.png\""  >> ${CAMERA}.gnuplot
  		echo "set xdata time"  >> ${CAMERA}.gnuplot
		echo "plot \"${CAMERA}.dat\" using 1:(\$2/\$3) title \"Red\", \"${CAMERA}.dat\" using 1:(\$4/\$5) title \"Green\", \"${CAMERA}.dat\" using 1:(\$6/\$7) title \"Blue\"" >> ${CAMERA}.gnuplot
		
		echo "$CAMERA gnuplot format done" > $TTY
	    fi

	    if [ \( ${CAMERA}.gnuplot -nt ${CAMERA}.png \) -o \
		\( ${CAMERA}.gnuplot -nt ${CAMERA}+spread.png \) -o \
		\( ${CAMERA}.gnuplot -nt ${CAMERA}+ratio.png \) ]
	    then
		gnuplot ${CAMERA}.gnuplot
		echo "$CAMERA gnuplot data created into ${CAMERA}.png" > $TTY
		echo "Spread for $CAMERA created in ${CAMERA}+spread.png" > $TTY
		echo "Ratios for $CAMERA created in ${CAMERA}+ratio.png" > $TTY
	    else
		echo "$CAMERA images were already up-to-date" > $TTY
	    fi
	done
    done
)

cd $OLDDIR
cat known-cameras.dxt | ( while read CAMERA
    do
	find . -name "${CAMERA}.dat" -exec cat '{}' ';' > "${CAMERA}.udat"
    	rm -f ${CAMERA}.ugnuplot
	echo "set output \"${CAMERA}.png\"" >> ${CAMERA}.ugnuplot
	echo 'set timefmt "%Y-%b-%d@%H:%M:%S"' >> ${CAMERA}.ugnuplot
	echo "set xdata time"  >> ${CAMERA}.ugnuplot
	echo "set term png" >> ${CAMERA}.ugnuplot
	echo "plot \"${CAMERA}.udat\" using 1:2:3 with yerrorlines title \"Red\", \"${CAMERA}.udat\" using 1:4:5 with yerrorlines title \"Green\", \"${CAMERA}.udat\" using 1:6:7 with yerrorlines title \"Blue\"" >> ${CAMERA}.ugnuplot
	echo "set output \"${CAMERA}+spread.png\""  >> ${CAMERA}.ugnuplot
	echo "set xdata"  >> ${CAMERA}.ugnuplot
	echo "plot \"${CAMERA}.udat\" using 2:3 title \"Red\", \"${CAMERA}.udat\" using 4:5 title \"Green\", \"${CAMERA}.udat\" using 6:7 title \"Blue\"" >> ${CAMERA}.ugnuplot
	echo "set output \"${CAMERA}+ratio.png\""  >> ${CAMERA}.ugnuplot
  	echo "set xdata time"  >> ${CAMERA}.ugnuplot
	echo "plot \"${CAMERA}.udat\" using 1:(\$2/\$3) title \"Red\", \"${CAMERA}.udat\" using 1:(\$4/\$5) title \"Green\", \"${CAMERA}.udat\" using 1:(\$6/\$7) title \"Blue\"" >> ${CAMERA}.ugnuplot
	echo "set output \"${CAMERA}+rgb+ratio.png\""  >> ${CAMERA}.ugnuplot
	echo "plot \"${CAMERA}.udat\" using 1:(\$2/\$4) title \"Red/Green\", \"${CAMERA}.udat\" using 1:(\$4/\$6) title \"Green/Blue\", \"${CAMERA}.udat\" using 1:(\$6/\$2) title \"Blue/Red\"" >> ${CAMERA}.ugnuplot
	echo -n "$CAMERA ugnuplot format done " > $TTY
	gnuplot ${CAMERA}.ugnuplot
	python $BASEDIR/balancepoint.py < ${CAMERA}.udat > ${CAMERA}.xdat
#	python $BASEDIR/everywhere.py < ${CAMERA}.udat > ${CAMERA}.ldat
#	python $BASEDIR/everywhere.py --average median < ${CAMERA}.udat > ${CAMERA}.mdat
	echo "data created into ${CAMERA}.png (and the usual other places)" > $TTY
    done
)
