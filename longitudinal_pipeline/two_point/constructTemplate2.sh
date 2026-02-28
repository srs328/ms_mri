#!/bin/bash

subid=$1
work_dir=$2

cd "$work_dir" || exit

antsMultivariateTemplateConstruction2.sh \
    -d 3 \
	-o "sub${subid}_" \
	-i 4 \
	-g 0.25 \
	-j 8 \
	-c 2 \
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


	# bsub -q short -o /home/shridhar.singh9-umw/logs/%J_%I.out -e /home/shridhar.singh9-umw/logs/%J_%I.err -u /dev/null -W 8:00 -n 6 -R "rusage[mem=5G
    
	# bsub -q short -o /home/shridhar.singh9-umw/logs/%J_%I.out -e /home/shridhar.singh9-umw/logs/%J_%I.err -u /dev/null -W 8:00 -n 6 -R "rusage[mem=2]"