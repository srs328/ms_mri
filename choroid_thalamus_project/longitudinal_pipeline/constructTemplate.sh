#!/bin/bash

subid=$1
work_dir=$2

cd "$work_dir" || exit

antsMultivariateTemplateConstruction2.sh \
    -d 3 -o "sub${subid}_" -r 1 t1_*_mniWarped.nii.gz
    