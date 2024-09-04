import os
import subprocess
from mri_preproc.paths import hemond_data

# dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataroot = "/mnt/h/3Tpioneer_bids"
dataset = hemond_data.get_raw_3Tpioneer_bids(dataroot, label_prefix="choroid_t1_flair", suppress_output=True)


for data in dataset:
    #if data.label is not None:
    merged_file = os.path.join(data.root, "t1_flair.nii.gz")
    if not os.path.exists(merged_file):
        merge_cmd_parts = ["fslmerge", "-a", merged_file, str(data.images['t1']), str(data.images['flair'])]
        print(" ".join(merge_cmd_parts))
        subprocess.run(merge_cmd_parts)
    else:
        print(f"Skipped {merged_file}")
        