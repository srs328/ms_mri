import os
import subprocess
from mri_preproc.paths import hemond_data
from mri_preproc.paths.hemond_data import DataSet

# dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataroot = "/mnt/h/3Tpioneer_bids"
# dataset = hemond_data.get_raw_3Tpioneer_bids(dataroot, label_prefix="choroid_t1_flair", suppress_output=True)
dataset: DataSet = hemond_data.scan_3Tpioneer_bids(dataroot, "flair", None)

subid = ""
for data in dataset:
    if data.subid == subid:
        continue
    else:
        subid = data.subid
    #if data.label is not None:
    merged_file = os.path.join(data.root, "t1_flair.nii.gz")
    if not os.path.exists(merged_file):
        t1_file = data.root / "t1.nii.gz"
        merge_cmd_parts = ["fslmerge", "-a", merged_file, str(t1_file), str(data.image)]
        print(" ".join(merge_cmd_parts))
        subprocess.run(merge_cmd_parts)
    else:
        print(f"Skipped {merged_file}")
        
