#!/bin/sh
#BSUB -J hipsthomas[1-629]%128
#BSUB -n 4
#BSUB -R "rusage[mem=5G]"
#BSUB -q short
#BSUB -W 8:00
#BSUB -o /home/shridhar.singh9-umw/logs/%J_%I.out
#BSUB -e /home/shridhar.singh9-umw/logs/%J_%I.err
#BSUB -u /dev/null

# Read the path for this task's index
path=$(sed -n "${LSB_JOBINDEX}p" /home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/subjects2.txt)

ml apptainer
cd $path
if [ -f sthomas_LR_labels.nii.gz ]; then
    echo "Output already exists, skipping: $path"
    exit 0
fi
apptainer exec --cleanenv --bind ${PWD}:/data \
    /home/shridhar.singh9-umw/hips-thomas.sif \
    /thomas/src/hipsthomas.sh -t1 -i t1.nii.gz
