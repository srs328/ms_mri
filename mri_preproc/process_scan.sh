#!/bin/bash

scan_dir=$1
prefix=$2


proc_dir=${scan_dir}/proc
if [[ ! -d "$proc_dir" ]]; then
    echo "making $proc_dir" 
    mkdir $proc_dir
fi

bet $scan_dir/$prefix.nii.gz $proc_dir/$prefix-brain.nii.gz -m -v

REF_DIR=$FSLDIR/data/standard

flirt -v \
    -in $proc_dir/$prefix-brain.nii.gz \
    -ref $REF_DIR/MNI152_T1_1mm \
    -omat $proc_dir/$prefix-affine.mat -dof 12

aff2rigid $proc_dir/$prefix-affine.mat $proc_dir/$prefix-rigid_affine.mat

flirt -v \
    -in $proc_dir/$prefix-brain.nii.gz \
    -ref $REF_DIR/MNI152_T1_1mm \
    -applyxfm -init $proc_dir/$prefix-rigid_affine.mat \
    -out $proc_dir/$prefix-brain-mni_space.nii.gz

