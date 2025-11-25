#!/bin/bash
# Transform your choroid segmentation to FreeSurfer space

SUBJECT=MNI152_T1_1mm1
SUBJECTS_DIR=/mnt/h/srs-9/fastsurfer/MNI152_T1_1mm1

# Your original segmentation (in native T1 space)
NATIVE_SEG=$1
side=$2

# FreeSurfer's conformed volume (the reference)
FS_REF=${SUBJECTS_DIR}/${SUBJECT}/mri/brain.mgz

# Output in FreeSurfer space
seg_stem=$(basename "$NATIVE_SEG" .nii.gz)
fs_seg="${SUBJECTS_DIR}/${SUBJECT}/mri/${seg_stem}.nii.gz"

# Method 1: If your segmentation is already aligned to the T1 you gave FreeSurfer
# (most common case - you segmented the same T1 that went into recon-all)
mri_convert \
    ${NATIVE_SEG} \
    ${fs_seg} \
    --like ${FS_REF} \
    -rt nearest  # Use nearest neighbor for label data

# Now tessellate in FreeSurfer space
mri_tessellate ${fs_seg} 1 ${SUBJECTS_DIR}/${SUBJECT}/surf/${side}.${seg_stem}.initial
mris_smooth -n 5 ${SUBJECTS_DIR}/${SUBJECT}/surf/${side}.${seg_stem}.initial \
    ${SUBJECTS_DIR}/${SUBJECT}/surf/${side}.${seg_stem}

#! This is what I defined on the fly when I did all of it through the terminal
# pipeline () {
#     vol=$1
#     mri_convert $thomas_home/$vol.nii.gz $mri_loc/$vol.nii.gz --like $mri_loc/brain.mgz -rt nearest
#     mri_tessellate $mri_loc/$vol.nii.gz 1 $surf_loc/lh.$vol.initial  
#     mris_smooth -n 5 $surf_loc/lh.$vol.initial $surf_loc/lh.$vol
# }
