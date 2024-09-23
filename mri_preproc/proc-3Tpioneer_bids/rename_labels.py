import os
from pathlib import Path
import shutil
import re
import subprocess
from mri_preproc.paths import hemond_data

# dataroot = Path("/mnt/e/3Tpioneer_bids")
# pit_label_home = Path("/mnt/e/pituitary_labels/final")

dataroot = Path("/media/smbshare/3Tpioneer_bids")

def get_subj_ses(filename):
    restr = re.compile(r"(sub-ms\d{4})_(ses-\d{8})\.nii\.gz")
    rematch = restr.match(filename.name)
    return rematch[1], rematch[2]

dataset = hemond_data.scan_3Tpioneer_bids(dataroot, "flair", None)

# for i in range(2):
#     label = labels[i]
i = 0
for scan in dataset:
    label = "pineal_srs.nii.gz"
    new_label = "pineal_SRS.nii.gz"
    label_path = scan.root / label
    new_label_path = scan.root / new_label
    if label_path.is_file():
        print(label_path, new_label_path)
        os.rename(label_path, new_label_path)
        i += 1

print(i)
