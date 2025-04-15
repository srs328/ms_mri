#!/bin/bash

subj_folder=$1

cd $subj_folder

docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i t1.nii.gz

docker stop $(docker ps -a -q)