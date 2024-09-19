import os
from pathlib import Path
import shutil
import re
import subprocess

# dataroot = Path("/mnt/e/3Tpioneer_bids")
# pit_label_home = Path("/mnt/e/pituitary_labels/final")

dataroot = Path("/media/smbshare/3Tpioneer_bids")
pit_label_home = Path("/media/hemondlab/Data/pituitary_labels/final")


def get_subj_ses(filename):
    restr = re.compile(r"(sub-ms\d{4})_(ses-\d{8})\.nii\.gz")
    rematch = restr.match(filename.name)
    return rematch[1], rematch[2]


labels = [
    Path(file.path)
    for file in os.scandir(pit_label_home)
    if file.name.split(".")[-1] == "gz"
]

# for i in range(2):
#     label = labels[i]
for label in labels:
    subj, ses = get_subj_ses(label)
    dest = dataroot / subj / ses / "pituitary.nii.gz"
    # shutil.copy2(label, dest)
    cp_cmd = ["cp", str(label), str(dest)]
    subprocess.run(cp_cmd)
