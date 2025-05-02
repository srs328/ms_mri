#!/bin/bash

scan=$1
viewport=$2 # "sagittal", "coronal", "axial"
save_path=$3
x=$4
y=$5
z=$6

coords=("$x" "$y" "$z")

freeview -v "$scan" --slice "${coords[@]}" --viewport "$viewport" --ss "$save_path" --layout 1 --viewsize 1920 1080
