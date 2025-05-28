#!/bin/bash

cd /home/srs-9/data_tmp/longitudinal/sub1042/20161013 || exit
docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i "sub1042_input0000-modality0-t1_20161013_mniWarped-WarpedToTemplate.nii.gz"

docker stop $(docker ps -a -q)

cd /home/srs-9/data_tmp/longitudinal/sub1042/20211029 || exit
docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i "sub1042_input0001-modality0-t1_20211029_mniWarped-WarpedToTemplate.nii.gz"
