#/bin/bash

#BSUB -J get_jacobians[1-186]
#BSUB -n 1
#BSUB -R "rusage[mem=4G]"
#BSUB -q short
#BSUB -W 2:00
#BSUB -o /home/shridhar.singh9-umw/logs/%J_%I.out
#BSUB -e /home/shridhar.singh9-umw/logs/%J_%I.err
#BSUB -u /dev/null

line=$(sed -n "${LSB_JOBINDEX}p" param_list_full.txt)
subject_root=$(echo $line | awk '{print $1}')
subid=$(echo $line | awk '{print $2}')
ses1=$(echo $line | awk '{print $3}')
ses2=$(echo $line | awk '{print $4}')

group_dir="$subject_root/group"

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
