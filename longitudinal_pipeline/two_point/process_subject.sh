#!/bin/bash
#BSUB -J jacobian_pipeline[28]%80
#BSUB -n 6
#BSUB -R "rusage[mem=5G]"
#BSUB -q short
#BSUB -W 8:00
#BSUB -o /home/shridhar.singh9-umw/logs/%J_%I.out
#BSUB -e /home/shridhar.singh9-umw/logs/%J_%I.err
#BSUB -u /dev/null

# running 957377 first 3 lines
source /home/shridhar.singh9-umw/Projects/ms_mri/.venv/bin/activate

export PATH=/home/shridhar.singh9-umw/ants-2.6.5/bin:$PATH
export FS_FREESURFERENV_NO_OUTPUT=false
export FREESURFER_HOME=$HOME/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# /home/shridhar.singh9-umw/data/longitudinal/sub1017 1017 20160921 20220118
line=$(sed -n "${LSB_JOBINDEX}p" param_list.txt)
subject_root=$(echo $line | awk '{print $1}')
subid=$(echo $line | awk '{print $2}')
ses1=$(echo $line | awk '{print $3}')
ses2=$(echo $line | awk '{print $4}')


# bash create_wmn_images.sh "$subject_root/$ses1"
# bash create_wmn_images.sh "$subject_root/$ses2"

group_dir="$subject_root/group"
if [ ! -d "$group_dir" ]; then
	mkdir $group_dir
fi

# cp "$subject_root/$ses1/t1_brain_wmn.nii.gz" "$group_dir/t1_brain_wmn_$ses1.nii.gz"
# cp "$subject_root/$ses2/t1_brain_wmn.nii.gz" "$group_dir/t1_brain_wmn_$ses2.nii.gz"

# files=(${group_dir}/*template0.nii.gz)
# if [ -e "${files[0]}" ]; then
if ! compgen -G "${group_dir}/*template0.nii.gz"; then
    bash constructTemplate.sh $subid $group_dir

fi

# fslstats sub1046_input0000-t1_brain_wmn_20181109-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
# fslstats sub1046_input0001-t1_brain_wmn_20210802-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
# fslstats sub1046_input0002-t1_brain_wmn_20220224-1Warp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M

# fslstats sub1046_input0000-t1_brain_wmn_20181109-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
# fslstats sub1046_input0001-t1_brain_wmn_20210802-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M
# fslstats sub1046_input0002-t1_brain_wmn_20220224-1InverseWarp-Jacobian00.nii.gz -k left/1-THALAMUS.nii.gz -M

ml apptainer
cd $group_dir
if [ -f sthomas_LR_labels.nii.gz ]; then
    echo "Thomas already exists, skipping"
    exit 0
fi
apptainer exec --cleanenv --bind ${PWD}:/data \
    /home/shridhar.singh9-umw/hips-thomas.sif \
    /thomas/src/hipsthomas.sh -i "sub${subid}_template0.nii.gz"
