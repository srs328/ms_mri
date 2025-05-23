#!/bin/bash

subjectFolder=$1
subid=$2

cd "$subjectFolder/$subid/mri" || exit
mri_convert orig.mgz orig.nii.gz
mri_convert orig/001.mgz orig/001.nii.gz

flirt -in orig.nii.gz -ref orig/001.nii.gz -omat freesurfer-to-subject.mat
