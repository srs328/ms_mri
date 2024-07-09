#!/bin/bash

data_dir=/mnt/t/brain/lesjak_2017/data
n_subj=$(find $data_dir -maxdepth 1 -type d -name "patient[0-9][0-9]" -printf . | wc -c)


for (( i = 1 ; i < 2 ; i++ )); do
	if [[ $i -lt 10 ]]
	then
		n="0$i"
	else
		n=$i
	fi
	subj_dir="$data_dir/patient$n"
	
	orig_dir="$subj_dir/raw"
	proc_dir="$subj_dir/proc"
	scan_prefix="patient${n}_FLAIR"
	
	if [ ! -d "$proc_dir" ]; then
		mkdir "$proc_dir"
	fi
	
	raw_file=$orig_dir/$scan_prefix.nii.gz
	
	# no CSF, border=1
	strip_file=$proc_dir/$scan_prefix.brain.nocsf.b1.nii.gz
	mask_file=$proc_dir/$scan_prefix.mask.nocsf.b1.nii.gz
	skull_file=$proc_dir/$scan_prefix.skull.csf.b1.nii.gz	
	
	mri_synthstrip \
	-i $raw_file \
	-o $strip_file --no-csf -b 1 
	
	fslmaths $mask_file \
	-sub 1 -mul -1 -mul $raw_file \
	$skull_file
	
	
	# no CSF, border=0
	strip_file=$proc_dir/$scan_prefix.brain.nocsf.b0.nii.gz
	mask_file=$proc_dir/$scan_prefix.mask.nocsf.b0.nii.gz
	skull_file=$proc_dir/$scan_prefix.skull.csf.b0.nii.gz
	
	mri_synthstrip \
	-i $raw_file \
	-o $strip_file --no-csf -b 0 
	
	fslmaths $mask_file \
	-sub 1 -mul -1 -mul $raw_file \
	$skull_file
	
	
	# CSF, border=1
	strip_file=$proc_dir/$scan_prefix.brain.csf.b1.nii.gz
	mask_file=$proc_dir/$scan_prefix.mask.csf.b1.nii.gz
	skull_file=$proc_dir/$scan_prefix.skull.nocsf.b1.nii.gz	
	
	mri_synthstrip \
	-i $raw_file \
	-o $strip_file -b 1 
	
	fslmaths $mask_file \
	-sub 1 -mul -1 -mul $raw_file \
	$skull_file
	
	
	# CSF, border=0
	strip_file=$proc_dir/$scan_prefix.brain.csf.b0.nii.gz
	mask_file=$proc_dir/$scan_prefix.mask.csf.b0.nii.gz
	skull_file=$proc_dir/$scan_prefix.skull.nocsf.b0.nii.gz
	
	mri_synthstrip \
	-i $raw_file \
	-o $strip_file -b 0 
	
	fslmaths $mask_file \
	-sub 1 -mul -1 -mul $raw_file \
	$skull_file
	
done


$prefix = $proc_dir/$scan_prefix

fslmaths $raw_file \
-mas $prefix.brain.csf.b0.nii.gz \
-mas $prefix.skull.csf.b1.nii.gz \
$prefix.csf.1.nii.gz

fslmaths $raw_file \
-mas $prefix.brain.csf.b1.nii.gz \
-mas $prefix.skull.csf.b0.nii.gz \
$prefix.csf.2.nii.gz

fslmaths $raw_file \
-mas $prefix.brain.csf.b0.nii.gz \
-mas $prefix.skull.csf.b0.nii.gz \
$prefix.csf.3.nii.gz

fslmaths $raw_file \
-mas $prefix.brain.csf.b1.nii.gz \
-mas $prefix.skull.csf.b1.nii.gz \
$prefix.csf.4.nii.gz
