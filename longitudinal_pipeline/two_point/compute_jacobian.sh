#!/bin/bash

# cd /home/shridhar.singh9-umw/data/longitudinal/sub2113/group2
# CreateJacobianDeterminantImage 3 sub1001_input0000-t1_brain_wmn_c-1InverseWarp.nii.gz sub1001_input0000-t1_brain_wmn_20170215-1InverseWarp-Jacobian00.nii.gz
# CreateJacobianDeterminantImage 3 sub1001_input0000-t1_brain_wmn_20170215-1Warp.nii.gz sub1001_input0000-t1_brain_wmn_20170215-1Warp-Jacobian00.nii.gz

# CreateJacobianDeterminantImage 3 sub1001_input0001-t1_brain_wmn_20200523-1InverseWarp.nii.gz sub1001_input0001-t1_brain_wmn_20200523-1InverseWarp-Jacobian00.nii.gz
# CreateJacobianDeterminantImage 3 sub1001_input0001-t1_brain_wmn_20200523-1Warp.nii.gz sub1001_input0001-t1_brain_wmn_20200523-1Warp-Jacobian00.nii.gz

# # CreateJacobianDeterminantImage 3 sub2113_input0002-t1_brain_wmn_20190213-1InverseWarp.nii.gz sub2113_input0002-t1_brain_wmn_20190213-1InverseWarp-Jacobian00.nii.gz
# # CreateJacobianDeterminantImage 3 sub2113_input0002-t1_brain_wmn_20190213-1Warp.nii.gz sub2113_input0002-t1_brain_wmn_20190213-1Warp-Jacobian00.nii.gz

# # CreateJacobianDeterminantImage 3 sub2113_input0003-t1_brain_wmn_20200107-1InverseWarp.nii.gz sub2113_input0003-t1_brain_wmn_20200107-1InverseWarp-Jacobian00.nii.gz
# # CreateJacobianDeterminantImage 3 sub2113_input0003-t1_brain_wmn_20200107-1Warp.nii.gz sub2113_input0003-t1_brain_wmn_20200107-1Warp-Jacobian00.nii.gz

# # CreateJacobianDeterminantImage 3 sub2113_input0004-t1_brain_wmn_20210314-1InverseWarp.nii.gz sub2113_input0004-t1_brain_wmn_20210314-1InverseWarp-Jacobian00.nii.gz
# # CreateJacobianDeterminantImage 3 sub2113_input0004-t1_brain_wmn_20210314-1Warp.nii.gz sub2113_input0004-t1_brain_wmn_20210314-1Warp-Jacobian00.nii.gz

# fslstats sub2113_input0000-t1_brain_wmn_20170126-1Warp-Jacobian00.nii.gz -k tthomas_tmp/left/1-THALAMUS.nii.gz -M
# fslstats sub2113_input0001-t1_brain_wmn_20180206-1Warp-Jacobian00.nii.gz -k tthomas_tmp/left/1-THALAMUS.nii.gz -M
# fslstats sub2113_input0002-t1_brain_wmn_20190213-1Warp-Jacobian00.nii.gz -k tthomas_tmp/left/1-THALAMUS.nii.gz -M
# fslstats sub2113_input0003-t1_brain_wmn_20200107-1Warp-Jacobian00.nii.gz -k tthomas_tmp/left/1-THALAMUS.nii.gz -M
# fslstats sub2113_input0004-t1_brain_wmn_20210314-1Warp-Jacobian00.nii.gz -k tthomas_tmp/left/1-THALAMUS.nii.gz -M


subid=$1
line=$(awk '$2 == "'$subid'"' param_list_full.txt)
ses1=$(echo $line | awk '{print $3}')
ses2=$(echo $line | awk '{print $4}')

group_dir="/home/srs-9/hpc/data/longitudinal/sub${subid}/group"

warp_ses1="sub${subid}_input0000-t1_brain_wmn_${ses1}-1Warp.nii.gz"
jac_warp_ses1="sub${subid}_input0000-t1_brain_wmn_${ses1}-1Warp-Jacobian00.nii.gz"
if [ ! -f "$group_dir/$warp_ses1" ]; then
    echo "$group_dir/$warp_ses1 does not exist" >&2
    exit 1
fi
if [ ! -f "$group_dir/$jac_warp_ses1" ]; then
    CreateJacobianDeterminantImage 3 "$group_dir/$warp_ses1" "$group_dir/$jac_warp_ses1"
fi


warp_ses2="sub${subid}_input0001-t1_brain_wmn_${ses2}-1Warp.nii.gz"
jac_warp_ses2="sub${subid}_input0001-t1_brain_wmn_${ses2}-1Warp-Jacobian00.nii.gz"
if [ ! -f "$group_dir/$warp_ses2" ]; then
    echo "$group_dir/$warp_ses2 does not exist" >&2
    exit 1
fi
if [ ! -f "$group_dir/$jac_warp_ses2" ]; then
    CreateJacobianDeterminantImage 3 "$group_dir/$warp_ses2" "$group_dir/$jac_warp_ses2"
fi

fslstats sub${subid}_input0000-t1_brain_wmn_${ses1}-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
fslstats sub${subid}_input0001-t1_brain_wmn_${ses2}-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M

fslstats -K left/thomasfull_L.nii.gz sub${subid}_input0000-t1_brain_wmn_${ses1}-1Warp-Jacobian00.nii.gz -M
fslstats -K left/thomasfull_L.nii.gz sub${subid}_input0001-t1_brain_wmn_${ses2}-1Warp-Jacobian00.nii.gz -M
