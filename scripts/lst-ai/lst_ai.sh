#!/bin/bash

source /home/srs-9/.virtualenvs/lst-ai/bin/activate

work_dir=$1
cd "$work_dir"

log="$work_dir/run_lst_ai.log"

exec > >(tee "$log") 2>&1
info() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" ; }


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

run_if_missing "$work_dir/lst-ai/space-flair_seg-lst.nii.gz" "
	lst --t1 t1.nii.gz --flair flair.nii.gz --output lst-ai --temp lst-ai/processing 
"