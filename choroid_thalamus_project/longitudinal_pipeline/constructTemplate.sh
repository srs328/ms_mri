#!/bin/bash

subid=$1
work_dir=$2

cd "$work_dir" || exit

antsMultivariateTemplateConstruction2.sh -d 3 -o "sub${subid}_" -r 1 t1_*_mniWarped.nii.gz
    

antsMultivariateTemplateConstruction2.sh \
    -d 3 \
    -o crop_t1_ \
    -i 4 \
    -g 0.25 \
    -j 4 \
    -c 0 \
    -k 1 \
    -w 1 \
    -f 8x4x2x1 \
    -s 3x2x1x0 \
    -q 100x70x50x10 \
    -n 1 \
    -r 1 \
    -m CC[4] \
    -t SyN \
    crop_t1_*.nii.gz