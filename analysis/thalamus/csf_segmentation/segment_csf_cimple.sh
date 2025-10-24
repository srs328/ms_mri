#!/bin/bash

root=$1

printf "running mri_synthstrip"
mri_synthstrip -i "$root/t1.nii.gz" -b 0 \
    -o "$root/t1.strip_b0.nii.gz"   

printf "running fast"
fast -N "$root/t1.strip_b0.nii.gz"
printf("done\n")

printf("extracting CSF from pveseg\n")
c3d "$root/*_pveseg.nii.gz" -retain-labels 1 -o "$root/all_CSF.nii.gz"

printf("creating peripheral_CSF mask\n")
fslmaths "$root/all_CSF.nii.gz" \
    -sub "$root/aseg-ventricles-fix.nii.gz" \
    -sub "$root/choroid.nii.gz" \
    -thr 0 -bin "$root/peripheral_CSF.nii.gz"   