import os
import subprocess
from mri_preproc.paths import hemond_data

# dataroot = "/home/hemondlab/3Tpioneer_bids"
dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataset = hemond_data.scan_3Tpioneer_bids(dataroot, "flair", "CLN_NL")

for data in dataset:
    orig_label = data.label
    new_label = data.root / "CLN_NL_1.nii.gz"
    if not new_label.is_file():
        binarize_cmd_parts = ["fslmaths", str(orig_label), "-bin", str(new_label)]
        print(" ".join(binarize_cmd_parts))
        subprocess.run(binarize_cmd_parts)
    else:
        print(f"Skipped {str(orig_label)}")