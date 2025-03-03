#!/bin/bash

label=$1
outdir=$2
postfix=$3

fslmaths $label -uthr 1 "$outdir/choroid-$postfix.nii.gz"
fslmaths $label -uthr 2 -thr 2 "$outdir/pineal-$postfix.nii.gz"
fslmaths $label -thr 3  "$outdir/pituitary-$postfix.nii.gz"
