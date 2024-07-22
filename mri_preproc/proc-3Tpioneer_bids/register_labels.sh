#!/bin/bash

# could make verbosity an optional parameter

scan_dir=$1
verbosity=${2:-0}

proc_dir="$scan_dir/proc"
affine="${proc_dir}/mni_reg-rigid_affine.mat"

REF_DIR=$FSLDIR/data/standard


if [[ ! -f "$affine" ]]; then
    mv "${proc_dir}/flair-mni_rigid_affine.mat" "$affine"
fi

# modalities=("phase" "t1" "t1_gd")

# for mod in ${modalities[@]}; do
#     raw_scan="${scan_dir}/${mod}.nii.gz"
#     reg_scan="${proc_dir}/${mod}
# done

for label in "$scan_dir"/lesion_index*; do
    label_prefix=${label%".nii.gz"}
    raw_label="${label_prefix}.nii.gz"
    reg_label="${label_prefix}-mni_reg.nii.gz"

    if [[ ! -f "$reg_label" ]]; then
        flirt -verbose "$verbosity" \
            -in "$raw_label" \
            -ref "$REF_DIR/MNI152_T1_1mm_brain.nii.gz" \
            -applyxfm -init "$affine" \
            -out "$reg_label"
    fi
done
