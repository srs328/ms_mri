#!/bin/bash

# could make verbosity an optional parameter

scan_dir=$1
verbosity=${2:-0}

proc_dir="$scan_dir/proc"
affine="${proc_dir}/mni_reg-rigid_affine.mat"

REF_DIR=$FSLDIR/data/standard


# modalities=("phase" "t1" "t1_gd")

# for mod in ${modalities[@]}; do
#     raw_scan="${scan_dir}/${mod}.nii.gz"
#     reg_scan="${proc_dir}/${mod}
# done

if [[ ! -f "$affine" ]]; then
    exit 1
fi

for label in "$scan_dir"/lesion_index*; do
    filename=$(basename "${label}")
    file_prefix=${filename%".nii.gz"}
    raw_label="${scan_dir}/${file_prefix}.nii.gz"    
    reg_label="${proc_dir}/${file_prefix}-mni_reg.nii.gz"

    if [[ ! -f "$reg_label" ]]; then
        echo "Applying affine transform to $raw_label"
        flirt -verbose "$verbosity" \
            -in "$raw_label" \
            -ref "$REF_DIR/MNI152_T1_1mm_brain.nii.gz" \
            -applyxfm -init "$affine" \
            -out "$reg_label"
    fi

    mask_label="${proc_dir}/${file_prefix}-mni_reg-mask.nii.gz"
    if [[ ! -f "$mask_label" ]]; then
        echo "Masking $reg_label"
        fslmaths "$reg_label" -div "$reg_label" "$mask_label"
    fi

done
