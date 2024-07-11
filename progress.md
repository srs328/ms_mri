# Plan

## Pipeline

1. Stack scans for each subject, save within subject directory as `\[SUBJ\]_stacked.nii.gz`

## Issues

- To stack the scans, I convert an nibabel image to a numpy array then stack. To resave as Nifi, I need to convert that image stack back to Nifti format and save. An nibabel image object has a header, affine, and dataobj attributes. I need to provide a value for affine when converting the stacked numpy array to nibabel image (or not? it's an optional parameter so maybe it doesn't matter). In the Lesjak data, the affine values are different for each scan of a subject. If this is the case for the Hemond data, I'll have to think about what to do.
    - They're similar enough in the Lesjak data that I could just pick any one. But I should look into the significance of the affine in case it's important and very sensitive to differences
- In the Lesjak data, the shapes of each nifti image within a subject are different. If this is the case with the Hemond data, I'll have to think about how to stack them. 
- Are the Hemond images registered within subjects?