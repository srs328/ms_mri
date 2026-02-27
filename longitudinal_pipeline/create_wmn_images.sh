#!/bin/bash

run_if_missing() {
    out="$1"; shift
    # treat empty or zero-size as missing
    if [[ -e "$out" && -s "$out" ]]; then
        info "SKIP: $out exists"
        return 0
    fi
    info "RUN: $* -> $out"
    if "$@"; then
        info "OK: produced $out"
    else
        info "ERROR: command failed: $*"
        return 1
    fi
}


subject_root=$1

remap_script=/home/srs-9/Projects/ms_mri/longitudinal_pipeline/wmnull/remap.py

t1_orig=$subject_root/t1.nii.gz
t1_mask=$subject_root/t1_mask.nii.gz
t1_brain=$subject_root/t1_brain.nii.gz

run_if_missing "$t1_brain" \
    mri_synthstrip -i "$t1_orig" -o "$t1_brain" -m "$t1_mask" -b 0 --gpu

t1_wmn=$subject_root/t1_brain_wmn.nii.gz
python $remap_script $t1_brain $t1_wmn
fslmaths $t1_wmn -mul $t1_mask $t1_wmn
