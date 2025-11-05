#!/usr/bin/env bash
export PATH=${FSLDIR}/share/fsl/bin:${PATH}
. ${FSLDIR}/etc/fslconf/fsl.sh
set -euo pipefail

orig=${1:-}
out_file=$2
out_dir=$(dirname "$out_file")
std_root=$3

log="$out_dir/transform_to_standard.log"
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

flirt -in "$orig" \
    -ref $std_root/t1_std.nii.gz -applyxfm -init $std_root/t1_std.mat \
    -o $out_file
