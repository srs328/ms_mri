#!/bin/bash

image=$1
affine=$2
out=$3

REF_DIR=$FSLDIR/data/standard

if [[ ! -f "$affine" ]]; then
    echo "Error: affine $affine doesn't exist " >&2
    exit 1
fi

if [[ ! -f "$image" ]]; then
    echo "Error: image $image doesn't exist " >&2
    exit 1
fi

echo "Applying affine transform to $image"
flirt -verbose 1 \
    -in "$image" \
    -ref "$REF_DIR/MNI152_T1_1mm_brain.nii.gz" \
    -applyxfm -init "$affine" \
    -out "$out"