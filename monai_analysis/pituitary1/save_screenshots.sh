#!/bin/bash

sub=$1
ses=$2

data_root=/mnt/h/3Tpioneer_bids
ensemble_root=/home/srs-9/Projects/ms_mri/training_work_dirs/cp_work_dir_pituitary1/ensemble_output/3Tpioneer_bids
save_dir=/home/srs-9/Projects/ms_mri/monai_analysis/pituitary1/screenshots

data_dir="$data_root/$sub/$ses"
ensemble_dir="$ensemble_root/$sub/$ses"

viewports=("sagittal" "coronal" "axial")
slice_coords=(120 177 118)

for i in {0..2}; do

    freeview -v "$data_dir/t1.nii.gz" \
        -v "$data_dir/pituitary.nii.gz":colormap=heat \
        --slice ${slice_coords[@]} --viewport ${viewports[i]} \
        --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_ground_truth.png" 

    # freeview -v "$data_dir/t1.nii.gz" \
    #     --slice ${slice_coords[@]} --viewport ${viewports[i]} \
    #     --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_unlabeled.png" 

    freeview -v "$data_dir/t1.nii.gz" \
        -v "$ensemble_dir/t1_ensemble.nii.gz":colormap=heat \
        --slice ${slice_coords[@]} --viewport ${viewports[i]} \
        --ss "$save_dir/$sub-$ses-${viewports[i]}${slice_coords[i]}_prediction.png" 

done

