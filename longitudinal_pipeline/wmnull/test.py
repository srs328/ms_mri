# %%

from remap import remap_image

#%%

input_image = "/home/shridhar.singh9-umw/data/longitudinal/sub1001/20170215/ocrop_t1.nii.gz"
output_image = "/home/shridhar.singh9-umw/data/longitudinal/sub1001/20170215/ocrop_t1_remap.nii.gz"

remap_image(input_image, output_image)