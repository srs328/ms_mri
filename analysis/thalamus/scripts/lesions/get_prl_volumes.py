#%%
import os
from pathlib import Path
import pandas as pd
import sys
import re
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
import pyperclip

sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")

import helpers
import utils

#%%
data = utils.load_data("/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv")
prl_data = pd.read_csv("/home/srs-9/Projects/ms_mri/data/PRL_labels.csv")

#%%

def subid_from_ID(id):
    return int(re.match(r"ms(\d{4,})", id)[1])
prl_data['subid'] = prl_data['ID'].map(subid_from_ID)
prl_data.set_index("subid", inplace=True)

#%% 
prl_data['all_prl_labels'] = [{"prl_labels": []} for subid in prl_data.index]
for subid in prl_data.index:
    total_prl = data.loc[subid, "PRL"]
    i = 1
    prl_labels = []
    prl_label = prl_data.loc[subid, f"PRL{i}_label"]
    while not pd.isna(prl_label):
        prl_labels.append(prl_label)
        i += 1
        prl_label = prl_data.loc[subid, f"PRL{i}_label"]

    prl_data.loc[subid, 'all_prl_labels']['prl_labels'] = prl_labels

# %%

def get_prl_label_for_subject(subid):
    total_prl = data.loc[subid, "PRL"]
    prl_labels = []
    for i in range(int(total_prl)):
        prl_label = prl_data.loc[subid, f"PRL{i+1}_label"]
        try:
            prl_labels.append(int(prl_label))
        except ValueError:
            print(subid, total_prl)
    return prl_labels

prl_data['prl_labels'] = prl_data.index.map(get_prl_label_for_subject)

# # I need to get only the definite ones, which I can do by only iterating n=PRL times
# prl_data['prl_labels'] = [{"prl_labels": []} for subid in prl_data.index]
# for subid in prl_data.index:
#     total_prl = data.loc[subid, "PRL"]
#     prl_labels = []
#     for i in range(int(total_prl)):
#         prl_label = prl_data.loc[subid, f"PRL{i+1}_label"]
#         prl_labels.append(prl_label)
#     prl_data.loc[subid, 'prl_labels']['prl_labels'] = prl_labels

#%%
import subprocess
from tqdm.notebook import tqdm

dataroot = Path("/mnt/h/3Tpioneer_bids")
lstat_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/scripts/PRL/lstats")
script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/scripts/PRL/save_lstat.sh"


no_lesion_file = []
for subid, row in tqdm(prl_data.iterrows(), total=len(prl_data)):

    subject_root = dataroot / f"sub-ms{subid}" / f"ses-{row['date_mri']}"
    t1 = subject_root / "t1.nii.gz"
    lesion_file = subject_root / "lesion.t3m20" / "lesion_index.t3m20.nii.gz"
    file = lstat_dir / f"lesion_vols-sub{subid}-{row['date_mri']}.csv"

    cmd = ["bash", script, str(t1), str(lesion_file), str(file)]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)


#%% 

def read_lesion_volumes(file):
    df = pd.read_csv(file, header=None, skiprows=1)
    df.columns = ['LabelID', 'Mean', 'StdD', 'Max', 'Min', 'Count', 
                'Vol(mm^3)', 'Extent_X', 'Extent_Y', 'Extent_Z']
    df['LabelID'] = df['LabelID'].map(int)
    df.set_index("LabelID", inplace=True)
    return df

subid = 1002
file = lstat_dir / f"lesion_vols-sub{subid}-{prl_data.loc[subid, 'date_mri']}.csv"
prl_labels = prl_data.loc[subid, 'prl_labels']
lesion_volumes = read_lesion_volumes(file)

total_vol = 0
for label in prl_labels:
    total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]

print(total_vol)