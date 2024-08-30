import os
import subprocess
from mri_preproc.paths import hemond_data

dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataset = hemond_data.get_raw_3Tpioneer_bids(dataroot, label_prefix="choroid_t1_flair", suppress_output=True)


for data in dataset:
    if data.label is not None:
        merged_file = os.path.join(data.root, "t1_flair.nii.gz")
        merge_cmd_parts = ["fslmerge", "-a", merged_file, str(data.images['t1']), str(data.images['flair'])]
        subprocess.run(merge_cmd_parts)
        