#!/bin/sh

# $Header$

export TZ=GMT

YEAR=$(date +%Y)
MON=$(date +%B)
DAY=$(date +%d)
HOUR=$(date +%H)
MINUTE=$(date +%M)

if [ ! -f ~/.camlocate.conf ]
then
  psql -d camlocate -q -t -A -F' ' -c 'select webcam_idx,shortname,url,directory from webcams where enabled;'  > ~/.camlocate.conf
fi

cat ~/.camlocate.conf |  ( while read webcam_idx shortname url directory
    do
	mkdir -p $(date +$directory)
	cd $(date +$directory)
	mkdir -p /tmp/camlocate/${shortname}
	LOG="/tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.log"
	FILENAME=${shortname}-${HOUR}:${MINUTE}.jpg
	wget --server-response $url -O $FILENAME > $LOG 2>&1 
	servertime=$(grep '  Date: ' $LOG | sed 's/  Date: //' | tail -1)
	lastmodified=$(grep '  Last-modified: ' $LOG | sed 's/  Last-modified: //' | tail -1)
	# Not all sites give this information. That's OK. We can cope.
	if [ "$lastmodified" = "" ]
	then
	    lastmodifiedcast=NULL
	else
	    lastmodifiedcast="cast('$lastmodified' as timestamp with time zone)"
	fi

	identify -verbose ${FILENAME} \
	    | grep -e '^      Mean:' -e '^      Standard deviation:' \
	    | sed 's/^.*(//' | sed 's/).*$//' |  tr '\n' ' ' \
	    > /tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.info 2> /tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.err
	if grep -q -e 'Corrupt JPEG data' /tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.err
	then
	    echo "${shortname}/${HOUR}:${MINUTE} had the following error: $(cat /tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.err)"
	    continue
	fi
	read redmean redstddev greenmean greenstddev bluemean bluestddev < /tmp/camlocate/${shortname}/${HOUR}:${MINUTE}.info
	num_colour=$(identify -quiet -format "%k" ${FILENAME})
	signature=$(identify -quiet -format "%#" ${FILENAME})

	echo "insert into images values (nextval('image_ids'),$webcam_idx,cast('$servertime' as timestamp with time zone),$lastmodifiedcast,'$FILENAME',$redmean,$bluemean,$greenmean,$redstddev,$greenstddev,$bluestddev,$num_colour,'$signature');" > ${shortname}-${HOUR}:${MINUTE}.sql	    
	#psql -q -d camlocate -f ${shortname}-${HOUR}:${MINUTE}.sql
    done
)


	    
