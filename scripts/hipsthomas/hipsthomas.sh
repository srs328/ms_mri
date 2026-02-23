#!/bin/bash

subj_folder=$1

cd $subj_folder

log="$subj_folder/hipsthomas.log"
# tee all output to a per-subject log
exec > >(tee -a "$log") 2>&1

docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i t1.nii.gz

docker stop $(docker ps -a -q)