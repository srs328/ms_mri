#!/bin/bash

set -euo pipefail

work_dir=$1

log="$work_dir/extract_aseg.log"
# tee all output to a per-subject log
exec > >(tee -a "$log") 2>&1

info() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" ; }

# run_if_missing() {
#     out="$1"; shift
#     # treat empty or zero-size as missing
#     if [[ -e "$out" && -s "$out" ]]; then
#         info "SKIP: $out exists"
#         return 0
#     fi
#     info "RUN: producing $out"
#     if bash -c "$*"; then
#         info "OK: produced $out"
#     else
#         info "ERROR: command failed: $*"
#         return 1
#     fi
# }

run_if_missing() {
    out="$1"
    shift
    if [[ -e "$out" && -s "$out" ]]; then
        echo "SKIP: $out exists"
        return 0
    fi
    echo "RUN: producing $out"
    if bash -c "$*"; then
        echo "OK: produced $out"
    else
        echo "ERROR: command block failed"
        return 1
    fi
}


cd "$work_dir"

# if [[ -e "$out" && -s "$out" ]];

run_if_missing "aseg-third_ventricle.nii.gz" "
	mri_extract_label "aseg.auto_noCCseg.in_subject.nii.gz" 14 "aseg-third_ventricle_tmp.nii.gz" &&
	c3d "aseg-third_ventricle_tmp.nii.gz" -connected-components -threshold 1 1 1 0 -o "aseg-third_ventricle.nii.gz" &&
	rm "aseg-third_ventricle_tmp.nii.gz"
"