#!/bin/bash
source $FREESURFER_HOME/SetUpFreeSurfer.sh
scan=$1
viewport=$2 # "sagittal", "coronal", "axial"
save_path=$3
x=$4
y=$5
z=$6

coords=("$x" "$y" "$z")
echo $scan
freeview -v "$scan:grayscale=0.0083,1.8" --slice "${coords[@]}" --viewport "$viewport" --ss "$save_path" --layout 1 --viewsize 1920 1080
# freeview -v "$scan" --slice "${coords[@]}" --viewport "$viewport" --layout 1 --viewsize 1920 1080
# freeview -v t1.nii.gz:grayscale=0.0083,1.8