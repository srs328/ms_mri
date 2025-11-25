# Notes

```shell
mri_tessellate $mri_loc/$vol.nii.gz 1 $surf_loc/lh.$vol.initial
mris_smooth -n 5 $surf_loc/lh.$vol.initial $surf_loc/lh.$vol
```