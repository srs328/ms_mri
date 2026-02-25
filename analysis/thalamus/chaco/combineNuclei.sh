#!/bin/bash

sub_root=$1

cd $sub_root

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

run_if_missing "thomas_ventral.nii.gz" \
    fslmaths thomas_thalamus.nii.gz -thr 2 -uthr 5 -bin thomas_ventral.nii.gz

run_if_missing "thomas_anterior.nii.gz" \
    fslmaths thomas_thalamus.nii.gz -uthr 1 -bin thomas_anterior.nii.gz

run_if_missing "thomas_posterior.nii.gz" \
    fslmaths thomas_thalamus.nii.gz -thr 6 -uthr 8 -bin thomas_posterior.nii.gz

run_if_missing "thomas_medial.nii.gz" \
    fslmaths thomas_thalamus.nii.gz -thr 9 -uthr 10 -bin thomas_medial.nii.gz