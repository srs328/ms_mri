#!/usr/bin/env bash
# ...existing code...
set -euo pipefail

root=${1:-}
if [[ -z "$root" || ! -d "$root" ]]; then
    echo "Usage: $0 /path/to/subject_root" >&2
    exit 2
fi

subject=$(basename "${root%/}")

log="$root/segment_csf.log"
# tee all output to a per-subject log (keep log in original root)
exec > >(tee -a "$log") 2>&1

info() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" ; }

# scratch dir under home
scratch_base="${HOME%/}/scratch"
scratch="${scratch_base}/${subject}"

# ensure cleanup and sync back on exit (success or failure)
on_exit() {
    rc=$?
    info "EXIT (code $rc) — syncing results from $scratch -> $root and removing scratch"
    if [[ -d "$scratch" ]]; then
        # copy everything back except the input t1 to avoid overwriting if undesired
        rsync -a --delete --exclude 't1.nii.gz' --exclude 'segment_csf.log' "$scratch/" "$root/" || info "WARN: rsync back failed"
        rm -rf "$scratch" || info "WARN: failed to remove $scratch"
    else
        info "No scratch dir to sync"
    fi
    exit "$rc"
}
trap on_exit EXIT

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

# prepare scratch
mkdir -p "$scratch"
info "Created scratch dir $scratch"

# copy the input t1 into scratch
if [[ -e "$root/t1.nii.gz" && -s "$root/t1.nii.gz" ]]; then
    rsync -a "$root/t1.nii.gz" "$scratch/" || { info "ERROR: copying t1 to scratch failed"; exit 1; }
else
    info "ERROR: input $root/t1.nii.gz missing or empty"; exit 2
fi

# run pipeline from scratch
cd "$scratch"

t1="$scratch/t1.nii.gz"

run_if_missing "$scratch/t1.strip_b0.nii.gz" \
    mri_synthstrip -i "$t1" -b 0 -o "$scratch/t1.strip_b0.nii.gz"

# fast produces files like <basename>_pveseg.nii.gz — check if any exist in scratch
shopt -s nullglob
pves=( "$scratch"/*_pveseg.nii.gz )
if [[ ${#pves[@]} -gt 0 ]]; then
    info "SKIP: pveseg outputs exist in scratch (${#pves[@]})"
else
    info "RUN: fast -N $scratch/t1.strip_b0.nii.gz"
    fast -N "$scratch/t1.strip_b0.nii.gz"
fi

run_if_missing "$scratch/all_CSF.nii.gz" \
    c3d "$scratch"/*_pveseg.nii.gz -retain-labels 1 -o "$scratch/all_CSF.nii.gz"

# subtract ventricular/choriod masks that live in original root
run_if_missing "$scratch/peripheral_CSF.nii.gz" \
    fslmaths "$scratch/all_CSF.nii.gz" \
        -sub "$root/aseg-lv-fix.nii.gz" \
        -sub "$root/aseg-rv-fix.nii.gz" \
        -sub "$root/choroid.nii.gz" \
        -thr 0 -bin "$scratch/peripheral_CSF.nii.gz"

info "DONE for $root (results in $scratch — will be synced back on exit)"
# ...existing code...