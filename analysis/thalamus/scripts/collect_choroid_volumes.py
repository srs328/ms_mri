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

choroid_name = "choroid.nii.gz"
all_csf_name = "all_CSF.nii.gz"
third_ventricle_name = "aseg-third_ventricle.nii.gz"
fourth_ventricle_name = "aseg-fourth_ventricle.nii.gz"
aseg_csf_name = "aseg-CSF.nii.gz"

with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")

all_subjects = [int(subid) for subid in list(subject_sessions.keys())]

subject_vols = {
    'subid': [],
    'choroid_volume': [],
}


# %%
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    subject_vols['subid'].append(int(subid))
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    data_dir = dataroot / f"sub{subid}-{sesid}"
    choroid_path = data_dir / choroid_name

    try:
        vol_stats = utils.compute_volume(str(choroid_path))
        if len(vol_stats) > 0:
            vol = vol_stats[1]
        else:
            print(subid, "error")
            vol = None
    except Exception as e:
        print(subid, e)
        vol = None
    subject_vols['choroid_volume'].append(vol)


df = pd.DataFrame(subject_vols)
df.set_index('subid', inplace=True)
df.index.name = "subid"

# %%
df.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/choroid_aschoplex_volumes.csv")


#%%

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/choroid_aschoplex_volumes.csv", index_col="subid")
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    subject_vols['subid'].append(int(subid))
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    data_dir = dataroot / f"sub{subid}-{sesid}"
    
    choroid_path = data_dir / "choroid_left.nii.gz"
    try:
        vol_stats = utils.compute_volume(str(choroid_path))
        if len(vol_stats) > 0:
            vol = vol_stats[1]
        else:
            print(subid, "error")
            vol = None
    except Exception as e:
        print(subid, e)
        vol = None
    df.loc[subid, "choroid_volume_left"] = vol

    choroid_path = data_dir / "choroid_right.nii.gz"
    try:
        vol_stats = utils.compute_volume(str(choroid_path))
        if len(vol_stats) > 0:
            vol = vol_stats[1]
        else:
            print(subid, "error")
            vol = None
    except Exception as e:
        print(subid, e)
        vol = None
    df.loc[subid, "choroid_volume_right"] = vol

# %%
df.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/choroid_aschoplex_volumes_bilateral.csv")

#%%
df2 = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/choroid_aschoplex_volumes.csv", index_col="subid")
for subid in df2.index:
    df2.loc[subid, "choroid_volume_left"] = df.loc[str(subid), "choroid_volume_left"]
    df2.loc[subid, "choroid_volume_right"] = df.loc[str(subid), "choroid_volume_right"]

#%%
df2.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/choroid_aschoplex_volumes_bilateral.csv")
