# Segmenting CSF/lymph channels

Can use cluster (forget which library it's part of) to segment continuous regions of a particular intensity and then pull out ROI's like the dorsal and ventral sinuses

- `cluster -i T:\brain\lesjak_2017\data\patient01\proc\patient01_FLAIR.csf.1.nii.gz -t 30`
- `fslmaths patient01_FLAIR.csf.1.clustered.nii.gz -thr 2080.5 -bin patient01_FLAIR.csf.1.clusteredLarge.nii.gz`
