#!/bin/bash

fastsurfer_dir=$1
hipsthomas_dir=$2

cd "$fastsurfer_dir/mri" || exit 

mri_convert aseg.auto_noCCseg.mgz aseg.auto_noCCseg.nii.gz
flirt -in aseg.auto_noCCseg.nii.gz -ref orig/001.nii.gz -applyxfm -init freesurfer-to-subject.mat -out "${hipsthomas_dir}/aseg.auto_noCCseg.in_subject.nii.gz"

cd "$hipsthomas_dir" || exit

fslmaths aseg.auto_noCCseg.in_subject.nii.gz -thr 4 -uthr 4 -bin aseg-lv.nii.gz
fslmaths aseg.auto_noCCseg.in_subject.nii.gz -thr 43 -uthr 43 -bin aseg-rv.nii.gz
fslmaths aseg-lv.nii.gz -add aseg-rv.nii.gz aseg-ventricles.nii.gz
c3d aseg-ventricles.nii.gz -sdt -o aseg-ventricles-sdt.nii.gz  