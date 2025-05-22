#!/bin/bash

subid=$1
work_dir=$2
cd $work_dir

t1_name="sub${subid}_template0.nii.gz"

docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i "$t1_name"

docker stop $(docker ps -a -q)