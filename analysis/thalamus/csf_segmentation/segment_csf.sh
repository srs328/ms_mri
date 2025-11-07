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




# Dilate ventricle mask for subtraction from peripheral CSF
kernal_shape="sphere"
kernal_size=2
out_suffix="_dilM_${kernal_shape}${kernal_size}"

prefix="aseg-lv-fix"
initial="${prefix}.nii.gz"
dilname="${prefix}${out_suffix}.nii.gz"
run_if_missing "$root/$dilname" \
    fslmaths "$root/$initial" -kernel $kernal_shape $kernal_size -dilM "$root/$dilname" 
lv_dilname=$dilname

prefix="aseg-rv-fix"
initial="${prefix}.nii.gz"
dilname="${prefix}${out_suffix}.nii.gz"
run_if_missing "$root/$dilname" \
    fslmaths "$root/aseg-rv-fix.nii.gz" -kernel $kernal_shape $kernal_size -dilM "$root/$dilname"
rv_dilname=$dilname

run_if_missing $root/aseg-lateral_ventricles.nii.gz \
	fslmaths $root/aseg-lv-fix.nii.gz -add $root/aseg-rv-fix.nii.gz $root/aseg-lateral_ventricles.nii.gz

run_if_missing $root/aseg-choroid.nii.gz \
	fslmaths $root/aseg-left_choroid.nii.gz -add $root/aseg-right_choroid.nii.gz $root/aseg-choroid.nii.gz

run_if_missing $root/aseg-lateral_ventricles_choroid.nii.gz \
	fslmaths $root/aseg-lateral_ventricles.nii.gz -add $root/aseg-choroid.nii.gz $root/aseg-lateral_ventricles_choroid.nii.gz

# Third Ventricle
kernal_shape="sphere"
kernal_size=2
out_suffix="_dilM_${kernal_shape}${kernal_size}"

prefix="aseg-third_ventricle"
initial="${prefix}.nii.gz"
dilname="${prefix}${out_suffix}.nii.gz"
# run_if_missing "$root/$dilname" \
#     fslmaths "$root/$initial" -kernel $kernal_shape $kernal_size -dilM "$root/$dilname" 
# thirdV_dilname=$dilname
thirdV_dilname=$initial

# CSF from aseg
kernal_shape="sphere"
kernal_size=2.2
out_suffix="_dilM_${kernal_shape}${kernal_size}"

prefix="aseg-CSF"
initial="${prefix}.nii.gz"
dilname="${prefix}${out_suffix}.nii.gz"
# run_if_missing "$root/$dilname" \
#     fslmaths "$root/$initial" -kernel $kernal_shape $kernal_size -dilM "$root/$dilname" 
# fsCSF_dilname=$dilname
fsCSF_dilname=$initial

# fourth ventricle
kernal_shape="sphere"
kernal_size=2
out_suffix="_dilM_${kernal_shape}${kernal_size}"

prefix="aseg-fourth_ventricle"
initial="${prefix}.nii.gz"
dilname="${prefix}${out_suffix}.nii.gz"
# run_if_missing "$root/$dilname" \
#     fslmaths "$root/$initial" -kernel $kernal_shape $kernal_size -dilM "$root/$dilname" 
# fourthV_dilname=$dilname
fourthV_dilname=$initial


run_if_missing "$root/peripheral_CSF_CHECK.nii.gz" \
fslmaths "$root/all_CSF.nii.gz" \
		-sub "$root/$lv_dilname" \
		-sub "$root/$rv_dilname" \
		-sub "$root/$thirdV_dilname" \
		-sub "$root/$fourthV_dilname" \
		-sub "$root/$fsCSF_dilname" \
		-sub "$root/choroid.nii.gz" \
		-thr 0 -bin "$root/peripheral_CSF_CHECK.nii.gz"


info "DONE for $root"
# ...existing code...