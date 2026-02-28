#!/bin/bash

#BSUB -n 36
#BSUB -q large
#BSUB -W 8:00
#BSUB -o "$HOME/%J.out"
#BSUB -e "$HOME/%J.err"

bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub2113/20180206
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub2113/20190213
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub2113/20200107
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub2113/20210314

echo "Done with wm null generation"

group_dir=/home/shridhar.singh9-umw/data/longitudinal/sub2113/group2
if [ ! -d "$group_dir" ]; then
	mkdir $group_dir
fi

ses=20170126
cp /home/shridhar.singh9-umw/data/longitudinal/sub2113/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20180206
cp /home/shridhar.singh9-umw/data/longitudinal/sub2113/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20190213
cp /home/shridhar.singh9-umw/data/longitudinal/sub2113/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20200107
cp /home/shridhar.singh9-umw/data/longitudinal/sub2113/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20210314
cp /home/shridhar.singh9-umw/data/longitudinal/sub2113/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz


cd "$group_dir" || exit
subid=2113

antsMultivariateTemplateConstruction2.sh \
    -d 3 \
	-o "sub${subid}_" \
	-i 4 \
	-g 0.25 \
	-j 6 \
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
    
