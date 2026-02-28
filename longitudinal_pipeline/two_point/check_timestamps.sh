#!/bin/bash

dataroot=/home/shridhar.singh9-umw/data/longitudinal
while read -r path id date1 date2; do
    group_dir="$path/group"
    sthomas_file=$group_dir/left/1-THALAMUS.nii.gz
    if [ ! -f $sthomas_file ]; then
        continue
    fi
    template_file=$group_dir/sub${id}_template0.nii.gz
    if [ $template_file -nt $sthomas_file ]; then
        echo $id
    fi
    # echo "Path: $path"
    # echo "ID: $id"
    # echo "Date1: $date1"
    # echo "Date2: $date2"
done < param_list_full.txt