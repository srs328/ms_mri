#!/bin/sh

subject_root=$1
subid=$2
ses1=$3
ses2=$4

bash create_wmn_images.sh "$subject_root/$ses1"
bash create_wmn_images.sh "$subject_root/$ses2"

group_dir="$subject_root/group"
if [ ! -d "$group_dir" ]; then
	mkdir $group_dir
fi

cp "$subject_root/$ses1/t1_brain_wmn.nii.gz" "$group_dir/t1_brain_wmn_$ses1"
cp "$subject_root/$ses2/t1_brain_wmn.nii.gz" "$group_dir/t1_brain_wmn_$ses2"

bash constructTemplate.sh $subid $group_dir

fslstats sub1046_input0000-t1_brain_wmn_20181109-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
fslstats sub1046_input0001-t1_brain_wmn_20210802-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
fslstats sub1046_input0002-t1_brain_wmn_20220224-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M

fslstats sub1046_input0000-t1_brain_wmn_20181109-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
fslstats sub1046_input0001-t1_brain_wmn_20210802-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
fslstats sub1046_input0002-t1_brain_wmn_20220224-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M