itksnap-wt -layers-set-main flair.nii.gz -tags-add FLAIR_MRI \
    -layers-add-anat t1.nii.gz -tags-add T1-MRI \
    -layers-add-seg choroid_t1_flair-CH.pineal-CH.pituitary-CH.nii.gz -tags-add choroid-pineal-pituitary-label \
    -layers-list -o /mnt/h/training_work_dirs/choroid_pineal_pituitary1/itksnap_workspaces/sub-ms1010-ses-20180208.itksnap