#!/usr/bin/env bash
# ...existing code...
set -euo pipefail

root=${1:-}
if [[ -z "$root" || ! -d "$root" ]]; then
    echo "Usage: $0 /path/to/subject_root" >&2
    exit 2
fi

subject=$(basename "$root")

log="$root/segment_csf.log"
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


t1="$root/t1.nii.gz"

# Skull strip
run_if_missing "$root/t1.strip_b0.nii.gz" \
    mri_synthstrip -i "$t1" -b 0 -o "$root/t1.strip_b0.nii.gz"

# Run FAST to get initial CSF segmentation
# fast produces files like <basename>_pveseg.nii.gz — check if any exist
shopt -s nullglob
pves=( "$root"/*_pveseg.nii.gz )
if [[ ${#pves[@]} -gt 0 ]]; then
    info "SKIP: pveseg outputs exist (${#pves[@]})"
else
    info "RUN: fast -N $root/t1.strip_b0.nii.gz"
    fast -N "$root/t1.strip_b0.nii.gz"
fi

run_if_missing "$root/all_CSF.nii.gz" \
    c3d "$root"/*_pveseg.nii.gz -retain-labels 1 -o "$root/all_CSF.nii.gz"

run_if_missing "$root/peripheral_CSF.nii.gz" \
    fslmaths "$root/all_CSF.nii.gz" \
        -sub "$root/aseg-lv.nii.gz" \
        -sub "$root/aseg-rv.nii.gz" \
        -sub "$root/choroid.nii.gz" \
        -thr 0 -bin "$root/peripheral_CSF.nii.gz"


# Dilate ventricle mask for subtraction from peripheral CSF
kernal_shape="sphere"
kernal_size=2
out_suffix="_dilM_${kernal_shape}${kernal_size}"
lv_dilname="aseg-lv${out_suffix}.nii.gz"
rv_dilname="aseg-rv${out_suffix}.nii.gz"

run_if_missing "$root/$lv_dilname" \
    fslmaths "$root/aseg-lv.nii.gz" -kernel $kernal_shape $kernal_size -dilM "$root/$lv_dilname" 

run_if_missing "$root/$rv_dilname" \
    fslmaths "$root/aseg-rv.nii.gz" -kernel $kernal_shape $kernal_size -dilM "$root/$rv_dilname"

peripheral_fix_name="peripheral_CSF${out_suffix}.nii.gz"
run_if_missing "$root/$peripheral_fix_name" \
    fslmaths "$root/peripheral_CSF.nii.gz" \
        -sub "$root/$lv_dilname" \
        -sub "$root/$rv_dilname" \
        -thr 0 -bin "$root/$peripheral_fix_name"


info "DONE for $root"
# ...existing code...