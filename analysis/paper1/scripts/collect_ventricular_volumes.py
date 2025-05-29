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


with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")

all_subjects = [int(subid) for subid in list(subject_sessions.keys())]

subject_vols = []
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    data_dir = dataroot / f"sub{subid}-{sesid}"
    seg_file = data_dir / "aseg-ventricles.nii.gz"

    try:
        vol_stats = utils.compute_volume(str(seg_file))
        if len(vol_stats) > 0:
            vol = vol_stats[1]
        else:
            print(subid, "error")
            vol = None
    except Exception:
        print(subid)
        vol = None
    subject_vols.append((int(subid), vol))

index = [item[0] for item in subject_vols]
vols = [item[1] for item in subject_vols]
df = pd.DataFrame({"ventricle_volume": vols}, index=index)
df.index.name = "subid"

# %%
df.to_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/ventricle_volumes.csv")