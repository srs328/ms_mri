#!/bin/bash

#BSUB -n 36
#BSUB -R "rusage[mem=4G]"
#BSUB -q short
#BSUB -W 8:00
#BSUB -o "$HOME/%J.out"
#BSUB -e "$HOME/%J.err"

bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub1495/20160918
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub1495/20171127
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub1495/20180627
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub1495/20190717
bash create_wmn_images.sh /home/shridhar.singh9-umw/data/longitudinal/sub1495/20210604

echo "Done with wm null generation"

group_dir=/home/shridhar.singh9-umw/data/longitudinal/sub1495/group2
if [ ! -d "$group_dir" ]; then
	mkdir $group_dir
fi

ses=20160918
cp /home/shridhar.singh9-umw/data/longitudinal/sub1495/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20171127
cp /home/shridhar.singh9-umw/data/longitudinal/sub1495/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20180627
cp /home/shridhar.singh9-umw/data/longitudinal/sub1495/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20190717
cp /home/shridhar.singh9-umw/data/longitudinal/sub1495/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz
ses=20210604
cp /home/shridhar.singh9-umw/data/longitudinal/sub1495/${ses}/t1_brain_wmn.nii.gz $group_dir/t1_brain_wmn_${ses}.nii.gz


cd "$group_dir" || exit
subid=1495

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
    
