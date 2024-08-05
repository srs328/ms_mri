#!/bin/bash

sub=$1
ses=$2

data_root=/mnt/t/Data/3Tpioneer_bids
ensemble_root=/home/srs-9/Projects/ms_mri/training_work_dirs/cp_work_dir22/ensemble_output
save_dir=/home/srs-9/Projects/ms_mri/monai_analysis/second-train/screenshots

data_dir="$data_root/$sub/$ses/proc"
ensemble_dir="$ensemble_root/$sub/$ses/proc"

viewports=("sagittal" "coronal" "axial")
slice_coords=(90 109 86)

for i in {0..2}; do

    freeview -v "$data_dir/flair-brain-mni_reg.nii.gz" \
        -v "$data_dir/lesion_index.t3m20-mni_reg-mask.nii.gz":colormap=binary \
        --slice ${slice_coords[@]} --viewport ${viewports[i]} \
        --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_ground_truth.png" 

    freeview -v "$data_dir/flair-brain-mni_reg.nii.gz" \
        --slice ${slice_coords[@]} --viewport ${viewports[i]} \
        --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_unlabeled.png" 

    freeview -v "$data_dir/flair-brain-mni_reg.nii.gz" \
        -v "$ensemble_dir/flair-brain-mni_reg_ensemble.nii.gz":colormap=binary \
        --slice ${slice_coords[@]} --viewport ${viewports[i]} \
        --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_prediction.png" 

done

