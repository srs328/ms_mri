#!/bin/bash

work_dir=$1
t1_name=$2

cd $work_dir || exit

docker run -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i "$t1_name"

if [ ! $? -eq 0 ]; then
    docker stop $(docker ps -a -q)
    exit 1
fi

docker stop $(docker ps -a -q)