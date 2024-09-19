import os
from pathlib import Path
import shutil
import re
import subprocess
from mri_preproc.paths import hemond_data
from mri_preproc.paths.hemond_data import Scan

# dataroot = Path("/mnt/e/3Tpioneer_bids")
# pit_label_home = Path("/mnt/e/pituitary_labels/final")

dataroot = Path("/media/smbshare/3Tpioneer_bids")
dest_dir = Path("/home/hemondlab/Dev/ms_mri/chp_seg/ins")

dataset = hemond_data.scan_3Tpioneer_bids(dataroot, 'flair', None)
dataset = sorted(dataset, key=lambda i: i.subid)


for i in range(100):
    scan: Scan = dataset[i]
    filename = f"sub-{scan.subid}-ses-{scan.date}.nii.gz"
    src = scan.image
    dst = dest_dir / filename
    print(src, dst)
    shutil.copy2(src, dst)

# for i in range(2):
# #     label = labels[i]
# for label in labels:
#     subj, ses = get_subj_ses(label)
#     dest = dataroot / subj / ses / "pituitary.nii.gz"
#     # shutil.copy2(label, dest)
#     cp_cmd = ["cp", str(label), str(dest)]
#     subprocess.run(cp_cmd)
