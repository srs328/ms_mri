#!/bin/bash

# could make verbosity an optional parameter

scan_dir=$1
prefix=$2
verbosity=${3:-0}


proc_dir="$scan_dir/proc"
if [[ ! -d "$proc_dir" ]]; then
    echo "making $proc_dir" 
    mkdir "$proc_dir"
fi

if [[ ! -f "$scan_dir/$prefix.nii.gz" ]]; then
    echo "No file $scan_dir/$prefix.nii.gz" > /dev/stderr
    exit 1 
fi

if [[ -f "$proc_dir/${prefix}-brain-mni_reg.nii.gz" ]]; then
    echo "$proc_dir/${prefix}-brain-mni_reg.nii.gz already exists"
    exit 0
fi

bet "$scan_dir/$prefix.nii.gz" "$proc_dir/${prefix}-brain.nii.gz" -m -v

REF_DIR=$FSLDIR/data/standard

flirt -verbose "$verbosity" \
    -in "$proc_dir/${prefix}-brain.nii.gz" \
    -ref "$REF_DIR/MNI152_T1_1mm_brain.nii.gz" \
    -omat "$proc_dir/${prefix}-mni_affine.mat" -dof 12

aff2rigid "$proc_dir/${prefix}-mni_affine.mat" "$proc_dir/${prefix}-mni_rigid_affine.mat"

flirt -verbose "$verbosity" \
    -in "$proc_dir/${prefix}-brain.nii.gz" \
    -ref "$REF_DIR/MNI152_T1_1mm_brain.nii.gz" \
    -applyxfm -init "${proc_dir}/${prefix}-mni_rigid_affine.mat" \
    -out "$proc_dir/${prefix}-brain-mni_reg.nii.gz"

echo "processing successful for $scan_dir/$prefix.nii.gz" > /dev/stderr


flirt \
  -in choroid.nii.gz \
  -ref "$REF_DIR/MNI152_T1_1mm.nii.gz" \
  -applyxfm -init "$aff" \
  -out "$out" \
  -interp nearestneighbour
