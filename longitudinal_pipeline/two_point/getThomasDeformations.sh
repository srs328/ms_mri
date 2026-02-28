#/bin/bash
#BSUB -J get_jacobians[18,29]
#BSUB -n 1
#BSUB -R "rusage[mem=2G]"
#BSUB -q short
#BSUB -W 8:00
#BSUB -o /home/shridhar.singh9-umw/logs/%J_%I.out
#BSUB -e /home/shridhar.singh9-umw/logs/%J_%I.err
#BSUB -u /dev/null

echo "Script start" 

source /home/shridhar.singh9-umw/Projects/ms_mri/.venv/bin/activate
FSLDIR=/home/shridhar.singh9-umw/fsl
PATH=${FSLDIR}/share/fsl/bin:${PATH}
export FSLDIR PATH
. ${FSLDIR}/etc/fslconf/fsl.sh

echo "Before line"
line=$(sed -n "${LSB_JOBINDEX}p" param_list_full.txt)
echo $line
subject_root=$(echo $line | awk '{print $1}')
subid=$(echo $line | awk '{print $2}')
ses1=$(echo $line | awk '{print $3}')
ses2=$(echo $line | awk '{print $4}')

file="$subject_root/group/sub${subid}_thomas_bilateral_deformations.csv"
echo $file
if [ -f $file ]; then
    echo "Already finished"
    exit 0
fi

echo $subid
bash thomasDeformationsCall.sh $subid