#!/bin/bash

kernal_shape="sphere"
kernal_size=2
work_dir=$1
cd $work_dir || exit 1

out_suffix="_dilM_${kernal_shape}${kernal_size}"
lv_outname="aseg-lv-fix${out_suffix}.nii.gz"
rv_outname="aseg-rv-fix${out_suffix}.nii.gz"

fslmaths aseg-lv-fix.nii.gz -kernel $kernal_shape $kernal_size -dilM $lv_outname
fslmaths aseg-rv-fix.nii.gz -kernel $kernal_shape $kernal_size -dilM $rv_outname

fslmaths "$work_dir/all_CSF.nii.gz" \
    -sub "$work_dir/$lv_outname" \
    -sub "$work_dir/$rv_outname" \
    -sub "$work_dir/choroid.nii.gz" \
    -thr 0 -bin "$work_dir/peripheral_CSF${out_suffix}.nii.gz"