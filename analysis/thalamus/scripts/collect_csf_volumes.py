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

peripheral_fix_name = "peripheral_CSF_dilM_sphere2.nii.gz"
all_csf_name = "all_CSF.nii.gz"
third_ventricle_name = "aseg-third_ventricle.nii.gz"

with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")

all_subjects = [int(subid) for subid in list(subject_sessions.keys())]

subject_vols = {'subid': [], 'peripheral': [], 'all': [], 'third_ventricle': []}
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    subject_vols['subid'].append(int(subid))
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    data_dir = dataroot / f"sub{subid}-{sesid}"
    peripheral_csf_file = data_dir / peripheral_fix_name
    all_csf_file = data_dir / all_csf_name
    third_ventricle_file = data_dir / third_ventricle_name

    for csf_type, csf_file in zip(
        ['all', 'peripheral', 'third_ventricle'],
        [all_csf_file, peripheral_csf_file, third_ventricle_file],
    ):
        try:
            vol_stats = utils.compute_volume(str(csf_file))
            if len(vol_stats) > 0:
                vol = vol_stats[1]
            else:
                print(subid, "error")
                vol = None
        except Exception as e:
            print(subid, e)
            vol = None
        subject_vols[csf_type].append(vol)


df = pd.DataFrame(subject_vols)
df.set_index('subid', inplace=True)
df.index.name = "subid"

# %%
df.to_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/csf_volumes.csv"
)
