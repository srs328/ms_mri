#!/bin/sh
#BSUB -J hipsthomas[1-629]%256
#BSUB -n 2
#BSUB -R "rusage[mem=8G]"
#BSUB -q short
#BSUB -W 8:00
#BSUB -o /home/shridhar.singh9-umw/logs/%J_%I.out
#BSUB -e /home/shridhar.singh9-umw/logs/%J_%I.err
#BSUB -u /dev/null

# Read the path for this task's index
path=$(sed -n "${LSB_JOBINDEX}p" /home/shridhar.singh9-umw/Projects/ms_mri/scripts/fsl_first/subjects2.txt)

cd $path
if [ -f t1-L_Thal_first.nii.gz ]; then
    echo "Output already exists, skipping: $path"
    exit 0
fi

run_first_all -dv -i t1.nii.gz -o t1 -s L_Thal,R_Thal
