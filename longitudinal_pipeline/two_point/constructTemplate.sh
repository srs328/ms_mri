#!/bin/bash
957398
source 
subid=$1
work_dir=$2

cd "$work_dir" || exit

antsMultivariateTemplateConstruction2.sh \
    -d 3 \
	-o "sub${subid}_" \
	-i 4 \
	-g 0.25 \
	-j 4 \
	-c 0 \
	-k 1 \
	-w 1 \
	-f 8x4x2x1 \
	-s 3x2x1x0 \
	-q 100x70x50x10 \
	-n 1 \
	-r 1 \
	-m CC[4] \
	-t SyN \
	t1_brain_wmn_*.nii.gz
    
	export PATH=/home/shridhar.singh9-umw/ants-2.6.5/bin:$PATH
export FS_FREESURFERENV_NO_OUTPUT=false
export FREESURFER_HOME=$HOME/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh