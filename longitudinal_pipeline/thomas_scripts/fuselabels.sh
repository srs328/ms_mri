#!/bin/bash
#
# Fuse all the thalamic and deep grey labels into one nii file.

if [ $# -lt 2 ]; then
    echo "Usage: $0 left|right nucleus# [nucleus#...]"
    exit 1
fi

# parse the required left/right argument
side=${1}; shift
if [ "$side" == "right" ]; then
    renum_factor=2
else
    renum_factor=1
fi
# echo "SIDE: $side, RENUM: $renum_factor"

# create empty base image files
fslmaths ${@:1:1}-* -mul 0 fused.nii.gz
fslmaths ${@:1:1}-* -mul 0 sfused.nii.gz

# fuse each of the given nucleus files to the base image files
for nuc_num in ${@:1}; do
    for nuc_file in ${nuc_num}-*; do
        echo "Fusing $nuc_file"
        fslmaths $nuc_file -mul $nuc_num nuc_label.nii.gz
        fslmaths $nuc_file -mul $renum_factor renum_label.nii.gz
        let renum_factor=$renum_factor+2
        ImageMath 3 fused.nii.gz overadd nuc_label.nii.gz fused.nii.gz
        ImageMath 3 sfused.nii.gz overadd renum_label.nii.gz sfused.nii.gz
    done
done

# rename the fused files, depending on side
if [ "$side" == "right" ]; then
    mv fused.nii.gz thomas_R.nii.gz
    mv sfused.nii.gz sthomas_R.nii.gz
    echo "Output written to thomas_R.nii.gz and sthomas_R.nii.gz"
else
    mv fused.nii.gz thomas_L.nii.gz
    mv sfused.nii.gz sthomas_L.nii.gz
    echo "Output written to thomas_L.nii.gz sthomas_L.nii.gz"
fi

# cleanup intermediate files
rm -f nuc_label.nii.gz renum_label.nii.gz
