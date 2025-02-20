#!/bin/bash

subj_dir=$1
orig_file=$2

mask_file="$subj_dir/$orig_file.mask.nii.gz" 

if [ ! -f $mask_file ]
then 
    mri_synthstrip -i "$subj_dir/$orig_file.nii.gz" -m "$subj_dir/$orig_file.mask.nii.gz"  --gpu
fi
# echo $subj_dir
# echo $orig_file