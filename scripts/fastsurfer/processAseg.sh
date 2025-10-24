#!/bin/bash

set -euo pipefail


fastsurfer_dir=$1
out_dir=$2

log="$out_dir/process_aseg.log"
# tee all output to a per-subject log
exec > >(tee -a "$log") 2>&1

info() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" ; }


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


cd "$fastsurfer_dir/mri" || exit 

run_if_missing "aseg.auto_noCCseg.nii.gz" \
    mri_convert aseg.auto_noCCseg.mgz aseg.auto_noCCseg.nii.gz

run_if_missing "orig/001.nii.gz" \
    mri_convert orig/001.mgz orig/001.nii.gz

run_if_missing "${out_dir}/aseg.auto_noCCseg.in_subject.nii.gz" \
    flirt -in aseg.auto_noCCseg.nii.gz -ref orig/001.nii.gz -applyxfm -init freesurfer-to-subject.mat -out "${out_dir}/aseg.auto_noCCseg.in_subject.nii.gz"

# fslmaths aseg.auto_noCCseg.in_subject.nii.gz -thr 4 -uthr 4 -bin aseg-lv.nii.gz
# fslmaths aseg.auto_noCCseg.in_subject.nii.gz -thr 43 -uthr 43 -bin aseg-rv.nii.gz
# fslmaths aseg-lv.nii.gz -add aseg-rv.nii.gz aseg-ventricles.nii.gz
# c3d aseg-ventricles.nii.gz -sdt -o aseg-ventricles-sdt.nii.gz  