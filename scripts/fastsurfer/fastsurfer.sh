#!/bin/bash

subid=$1
subj_folder=$2
output_folder=$3

fs_license=/home/srs-9

# 2. Run command
docker run --gpus all -v $subj_folder:/data \
                      -v $output_folder:/output \
                      -v $fs_license:/fs_license \
                      --rm --user $(id -u):$(id -g) deepmi/fastsurfer:latest \
                      --fs_license /fs_license/license.txt \
                      --t1 /data/t1.nii.gz \
                      --sid $subid --sd /output \
                      --3T \
                      --threads 4 \
                      --seg_only


                      