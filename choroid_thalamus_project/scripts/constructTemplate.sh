#!/bin/bash

subid=$1
work_dir=$2

cd "$work_dir" || exit

antsMultivariateTemplateConstruction2.sh \
    -d 3 -o "sub${subid}_" -z /home/srs-9/fsl/data/standard/MNI152_T1_1mm.nii.gz -r 1 t1_*
    