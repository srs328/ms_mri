#!/usr/bin/env bash

root=${1:-}


dilMethod="dilF"

kernal_shape="boxv"

kernal_size=1
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=3
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"


fslmaths "aseg-lv-fix.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"


# -------------

kernal_shape="sphere"

kernal_size=1
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=2
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=2.01
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=2.05
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=2.1
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"

kernal_size=2.2
out_suffix="_${dilMethod}_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv-fix${out_suffix}.nii.gz"
fslmaths "$root/aseg-lv.nii.gz" -kernel $kernel_shape $kernel_size -$dilMethod "$root/$lv_dilname"
