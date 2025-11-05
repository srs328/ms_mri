# %%
import pandas as pd
from loguru import logger
from pathlib import Path
from tqdm import tqdm
import os
import re
import sys
import json
from mri_data import utils
import subprocess

peripheral_fix_name = "peripheral_CSF_CHECK.nii.gz"
all_csf_name = "all_CSF.nii.gz"
third_ventricle_name = "aseg-third_ventricle.nii.gz"
fourth_ventricle_name = "aseg-fourth_ventricle.nii.gz"
aseg_csf_name = "aseg-CSF.nii.gz"

with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

pioneer_bids_root = Path("/mnt/h/3Tpioneer_bids")
dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
qc_root = Path("/mnt/h/srs-9/thalamus_project/qc")
all_subjects = [int(subid) for subid in list(subject_sessions.keys())]
script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/quality_control/to_standard.sh"

vols_to_convert = [
    "choroid",
    "aseg-ventricles",
    "aseg-third_ventricle",
    "aseg-fourth_ventricle",
    "aseg-CSF",
    "peripheral_CSF_CHECK",
    "all_CSF"
]

# %%

i = 0
for sub, sessions in subject_sessions.items():
    ses = sessions[0]
    if i > 5:
        break
    subject_root = dataroot / f"sub{sub}-{ses}"
    target_root = qc_root / f"sub{sub}-{ses}"
    if not target_root.exists():
        os.makedirs(target_root)
    std_root = pioneer_bids_root / f"sub-ms{sub}" / f"ses-{ses}" / "proc"
    
    for vol in vols_to_convert:
        orig = subject_root / f"{vol}.nii.gz"
        out_file = target_root / f"{vol}_std.nii.gz"
        
        cmd = [script, str(orig), str(out_file), str(std_root)]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(e)
            raise e 
    i += 1
    