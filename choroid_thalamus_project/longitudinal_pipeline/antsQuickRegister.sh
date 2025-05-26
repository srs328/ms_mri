#!/bin/bash

sesid=$1
work_dir=$2
cd "$work_dir" || exit

mni=/usr/local/fsl/data/standard/MNI152_T1_1mm.nii.gz
# mni=~/fsl/data/standard/MNI152_T1_1mm.nii.gz

antsRegistrationSyNQuick.sh -d 3 -t r -f $mni -m "t1_${sesid}.nii.gz" -o "t1_${sesid}_mni"