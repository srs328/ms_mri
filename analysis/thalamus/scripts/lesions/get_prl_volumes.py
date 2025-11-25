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
import subprocess
from tqdm.notebook import tqdm
from loguru import logger

sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")

import helpers
import utils


#%% Settings
produce_lstats = True


#%%
dataroot = Path("/mnt/h/3Tpioneer_bids")
lstat_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/scripts/lesions/lstats")
script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/scripts/lesions/save_lstat.sh"

data = utils.load_data("/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv")
prl_data = pd.read_csv("/home/srs-9/Projects/ms_mri/data/PRL_labels.csv")

#%%

def subid_from_ID(id):
    return int(re.match(r"ms(\d{4,})", id)[1])
prl_data['subid'] = prl_data['ID'].map(subid_from_ID)
prl_data.set_index("subid", inplace=True)

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

def get_all_prl_labels_for_subject(subid):
    prl_labels = []
    num_na = 0
    for i in range(20):
        if num_na >= 3:
            break
        prl_label = prl_data.loc[subid, f"PRL{i+1}_label"]
        if pd.isna(prl_label):
            num_na += 1
            continue
        prl_labels.append(int(prl_label))

    return prl_labels

prl_data['prl_labels'] = prl_data.index.map(get_prl_label_for_subject)
prl_data['all_prl_labels'] = prl_data.index.map(get_all_prl_labels_for_subject)


#%%
subid = 1052
subject_root = dataroot / f"sub-ms{subid}" / f"ses-{prl_data.loc[subid, 'date_mri']}"
# lesion_path = subject_root / "lesion.t3m20/mlesion_index.t3m20.nii.gz"
lesion_path = subject_root / "lesion.t3m20/lesion_index.t3m20.nii.gz"
# lesion_path = subject_root / "lesion.t3m20/mlesion_centers.nii.gz"


lesion_image = nib.load(lesion_path).get_fdata()
print(data.loc[subid, 'PRL'])
print(np.unique(lesion_image))
print(prl_data.loc[subid, "prl_labels"])

#%%

columns = ['LabelID', 'Mean', 'StdD', 'Max', 'Min', 'Count', 
                'Vol(mm^3)', 'Extent_X', 'Extent_Y', 'Extent_Z']

check_files = [
    "lesion.t3m20/mlesion_index.t3m20.nii.gz",
    "lesion.t3m20/lesion_centers.nii.gz",
    "lesion.t3m20/centerlesion_analysis/lesion_centers.nii.gz",
    "lesion.t3m20/mlesion_centers.nii.gz",
    "lesion.t3m20/centerlesion_analysis/mlesion_centers.nii.gz",
    "lesion.t3m20/lesion_index.t3m20.nii.gz"
]

produce_lstats = True
if produce_lstats:
    no_lesion_file = []
    for subid, row in tqdm(prl_data.iterrows(), total=len(prl_data)):
        subject_root = dataroot / f"sub-ms{subid}" / f"ses-{row['date_mri']}"
        t1 = subject_root / "t1.nii.gz"

        for file in check_files:
            lesion_file = subject_root / file
            if lesion_file.exists():
                break
        
        out_file = lstat_dir / f"lesion_vols-sub{subid}-{row['date_mri']}.csv"

        cmd = ["bash", script, str(lesion_file), str(lesion_file), str(out_file)]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(e.stderr)

        try:
            df = pd.read_csv(out_file, header=None, skiprows=1)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=columns)
        else:
            df.columns = columns
            df['LabelID'] = df['LabelID'].map(int)
        df.set_index("LabelID", inplace=True)
        df.to_csv(out_file)


#%% 

prl_data['PRL_volume'] = 0
prl_data['PRL_all_volume'] = 0
failed_subs = set()
for subid, _ in prl_data.iterrows():
    subject_root = dataroot / f"sub-ms{subid}" / f"ses-{prl_data.loc[subid, 'date_mri']}"
    file = lstat_dir / f"lesion_vols-sub{subid}-{prl_data.loc[subid, 'date_mri']}.csv"
    lesion_volumes = pd.read_csv(file, index_col="LabelID")

    # try:
    prl_labels = prl_data.loc[subid, 'prl_labels']
    total_vol = 0
    # for label in prl_labels:
    #     try:
    #         total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]
    #     except KeyError:
    #         logger.warning(f"sub{subid}, label={label}")

    #         if subid not in failed_subs:
    #             logger.debug(str(subject_root))
    #         failed_subs.add(subid)
    # prl_data.loc[subid, 'PRL_volume'] = total_vol

    prl_labels = prl_data.loc[subid, 'all_prl_labels']
    total_vol = 0
    for label in prl_labels:
        try:
            total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]
        except KeyError:
            # logger.warning(f"sub{subid}, label={label}")
            check_path = subject_root / "lesion.t3m20/lesion_centers.nii.gz"
            if check_path.exists():
                # logger.info(f'Lesion centers exist: {str(check_path)}')
                pass
            else:
                check_folder = subject_root / "lesion.t3m20/centerlesion_analysis"
                check_path = check_folder / "lesion_centers.nii.gz"
                if check_path.exists():
                    pass
                else:
                    logger.error(f'Lesion centers missing: {str(check_path)}')
                    if subid not in failed_subs:
                        logger.debug(str(subject_root))
                    failed_subs.add(subid)
    prl_data.loc[subid, 'PRL_all_volume'] = total_vol


failed_subs = list(set(failed_subs))
print(len(failed_subs))
print(failed_subs)
    
# %%
prl_data['PRL_volume'] = 0
prl_data['PRL_all_volume'] = 0
failed_subs = set()
for subid, _ in prl_data.iterrows():
    subject_root = dataroot / f"sub-ms{subid}" / f"ses-{prl_data.loc[subid, 'date_mri']}"
    file = lstat_dir / f"lesion_vols-sub{subid}-{prl_data.loc[subid, 'date_mri']}.csv"
    lesion_volumes = pd.read_csv(file, index_col="LabelID")

    # try:
    prl_labels = prl_data.loc[subid, 'prl_labels']
    total_vol = 0
    # for label in prl_labels:
    #     try:
    #         total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]
    #     except KeyError:
    #         logger.warning(f"sub{subid}, label={label}")

    #         if subid not in failed_subs:
    #             logger.debug(str(subject_root))
    #         failed_subs.add(subid)
    # prl_data.loc[subid, 'PRL_volume'] = total_vol

    prl_labels = prl_data.loc[subid, 'prl_labels']
    total_vol = 0
    for label in prl_labels:
        try:
            total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]
        except KeyError:
            logger.error(f"sub{subid}, label={label}")
            failed_subs.add(subid)
    prl_data.loc[subid, 'PRL_all_volume'] = total_vol


print(len(failed_subs))
print(failed_subs)

# %%

# %%
prl_data['PRL_volume'] = None
failed_subs = set()
for subid, _ in prl_data.iterrows():
    subject_root = dataroot / f"sub-ms{subid}" / f"ses-{prl_data.loc[subid, 'date_mri']}"
    file = lstat_dir / f"lesion_vols-sub{subid}-{prl_data.loc[subid, 'date_mri']}.csv"
    lesion_volumes = pd.read_csv(file, index_col="LabelID")

    
    prl_labels = prl_data.loc[subid, 'prl_labels']
    total_vol = 0
    for label in prl_labels:
        try:
            total_vol += lesion_volumes.loc[label, "Vol(mm^3)"]
        except KeyError:
            logger.error(f"sub{subid}, label={label}")
            failed_subs.add(subid)
            total_vol = None
            break
    prl_data.loc[subid, 'PRL_volume'] = total_vol


print(len(failed_subs))
print(sorted(list(failed_subs)))

# %%

data['PRL_volume'] = prl_data['PRL_volume']
data.loc[data['PRL'] == 0, 'PRL_volume'] = 0
save_data = data[['PRL_volume']]
save_data.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/prl_volumes.csv")