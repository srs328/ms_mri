#!/bin/bash

sub_root=$1

cd $sub_root || exit

run_if_missing() {
    out="$1"; shift
    # treat empty or zero-size as missing
    if [[ -e "$out" && -s "$out" ]]; then
        echo "SKIP: $out exists"
        return 0
    fi
    echo "RUN: $* -> $out"
    if "$@"; then
        echo "OK: produced $out"
    else
        echo "ERROR: command failed: $*"
        return 1
    fi
}

cd left || exit 

run_if_missing "thomas_posterior.nii.gz" \
    fslmaths 8-Pul.nii.gz -add 9-LGN.nii.gz -add 10-MGN.nii.gz thomas_posterior.nii.gz

run_if_missing "thomas_medial.nii.gz" \
    fslmaths 11-CM.nii.gz -add 12-MD-Pf.nii.gz thomas_medial.nii.gz

cp "4567-VL.nii.gz" "thomas_ventral.nii.gz"
cp "2-AV.nii.gz" "thomas_anterior.nii.gz"
cp "CL_L.nii.gz" "15-CL.nii.gz"


cd ../right || exit

run_if_missing "thomas_posterior.nii.gz" \
    fslmaths 8-Pul.nii.gz -add 9-LGN.nii.gz -add 10-MGN.nii.gz thomas_posterior.nii.gz

run_if_missing "thomas_medial.nii.gz" \
    fslmaths 11-CM.nii.gz -add 12-MD-Pf.nii.gz thomas_medial.nii.gz

cp "4567-VL.nii.gz" "thomas_ventral.nii.gz"
cp "2-AV.nii.gz" "thomas_anterior.nii.gz"
cp "CL_R.nii.gz" "15-CL.nii.gz"


cd $sub_root || exit

mkdir -p bilateral

KEY_REF=(
    "1-THALAMUS.nii.gz"
    "10-MGN.nii.gz"
    "11-CM.nii.gz"
    "12-MD-Pf.nii.gz"
    "13-Hb.nii.gz"
    "14-MTT.nii.gz"
    "2-AV.nii.gz"
    "26-Acc.nii.gz"
    "27-Cau.nii.gz"
    "28-Cla.nii.gz"
    "29-GPe.nii.gz"
    "30-GPi.nii.gz"
    "31-Put.nii.gz"
    "32-RN.nii.gz"
    "33-GP.nii.gz"
    "34-Amy.nii.gz"
    "4-VA.nii.gz"
    "4567-VL.nii.gz"
    "5-VLa.nii.gz"
    "6-VLP.nii.gz"
    "6_VLPd.nii.gz"
    "6_VLPv.nii.gz"
    "7-VPL.nii.gz"
    "8-Pul.nii.gz"
    "9-LGN.nii.gz"
	"thomas_anterior.nii.gz"
	"thomas_ventral.nii.gz"
	"thomas_medial.nii.gz"
	"thomas_posterior.nii.gz"
    "15-CL.nii.gz"
)

for item in "${KEY_REF[@]}"; do
	run_if_missing "bilateral/$item" \
	    fslmaths "left/$item" -add "right/$item" "bilateral/$item"
done
