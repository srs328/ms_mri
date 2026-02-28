# %%
import pandas as pd
import csv
from tqdm import tqdm
from datetime import datetime
from loguru import logger
import re
import os
from statistics import mean
from pathlib import Path
import subprocess
import sys


# %%

now = datetime.now()
log_filename = now.strftime(
    f"{os.path.basename(__file__).split('.')[0]}-%Y%m%d_T%H%M%S.log"
)
logger.remove()
logger.add(log_filename, mode="w")
logger.add(sys.stderr)

dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
subject_sessions = pd.read_csv("longitudinal_sessions.csv", index_col="subid")
data_dir = Path("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline") / "data0"


# %% Functions for parsing the nucleiVols.txt files

def parse_hipsthomas_vols(file):
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=" ")
        vols = {row[0]: float(row[1]) for row in reader}
    return vols


def get_hipsthomas_vols(loc):
    left_vols = parse_hipsthomas_vols(os.path.join(loc, "left", "nucleiVols.txt"))
    right_vols = parse_hipsthomas_vols(os.path.join(loc, "right", "nucleiVols.txt"))
    # vols = {key: left_vols[key] + right_vols[key] for key in left_vols}
    return left_vols, right_vols

def fslstats(mask_file, stat_flags, index_mask=None):
    """
    Run fslstats and return results as a list of floats.
    
    Parameters
    ----------
    mask_file : str
        Path to the input image
    stat_flags : str or list
        Stats flags e.g. '-M' or ['-M', '-S']
    index_mask : str, optional
        Path to index mask file (for -K option)
    
    Returns
    -------
    list of float (single stat) or list of lists (multiple stats per label)
    """
    if isinstance(stat_flags, str):
        stat_flags = stat_flags.split()
    
    cmd = ['fslstats']
    if index_mask:
        cmd += ['-K', index_mask]
    cmd += [mask_file] + stat_flags
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    
    parsed = []
    for line in lines:
        values = [float(v) for v in line.split()]
        parsed.append(values[0] if len(values) == 1 else values)
    
    return parsed



# %%
for subid, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    subject = f"sub{subid}"
    subject_root = dataroot / subject
    ses1, ses2 = int(row['ses1']), int(row['ses2'])

    ses1_folder = subject_root / str(ses1)
    left_file = ses1_folder / "t1-L_Thal_first.nii.gz"
    right_file = ses1_folder / "t1-R_Thal_first.nii.gz"
    if not left_file.exists() or not right_file.exists():
        print(f"No results for sub{subid} ses{ses1}")

    ses2_folder = subject_root / str(ses2)
    left_file = ses2_folder / "t1-L_Thal_first.nii.gz"
    right_file = ses2_folder / "t1-R_Thal_first.nii.gz"
    if not left_file.exists() or not right_file.exists():
        print(f"No results for sub{subid} ses{ses2}")


# %%


all_left_data = []
all_right_data = []
all_full_data = []
continue_subject = False
subject_index = []
for subid, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    subject = f"sub{subid}"
    subject_root = dataroot / subject
    ses1, ses2 = str(int(row['ses1'])), str(int(row['ses2']))

    left_data = {}
    right_data = {}
    full_data = {}

    ses_num = 1
    for ses in [ses1, ses2]:
        ses_root = subject_root / str(ses)
        left_path_first = ses_root / "t1-L_Thal_first.nii.gz"
        right_path_first = ses_root / "t1-R_Thal_first.nii.gz"
        if (
            not left_path_first.exists()
            or not right_path_first.exists()
        ):
            continue

        left_data[f"time{ses_num}"] = right_data[f"time{ses_num}"] = full_data[
            f"time{ses_num}"
        ] = ses
        
        left_path = ses_root / "t1-L_Thal.nii.gz"
        right_path = ses_root / "t1-R_Thal.nii.gz"
        
        try:
            if not left_path.exists():
                subprocess.run(["bash", "fslmaths", left_path_first, "-uthr", "60", left_path])
            if not right_path.exists():
                subprocess.run(["bash", "fslmaths", right_path_first, "-uthr", "60", right_path])
        except subprocess.CalledProcessError as e:
            logger.warning(subid)
            logger.error(e.stderr)
            continue

        # Handle some errors
        try:
            left_vol = fslstats(left_path, "-V")[0][1]
            right_vol = fslstats(right_path, "-V")[0][1]
        except Exception as e:
            logger.warning(f"Missing something for {subject} in session {ses}")
            logger.error(e)
            continue_subject = True
            break
        

        left_data[f"thalamus_time{ses_num}"] = left_vol
        right_data[f"thalamus_time{ses_num}"] = right_vol
        full_data[f"thalamus_time{ses_num}"] = left_vol + right_vol

        ses_num += 1
    
    if continue_subject:
        continue_subject = False
        continue

    all_left_data.append(left_data)
    all_right_data.append(right_data)
    all_full_data.append(full_data)
    subject_index.append(subid)

# %%

df_left = pd.DataFrame(all_left_data, index=subject_index)
df_left.index.name = "subid"
df_right = pd.DataFrame(all_right_data, index=subject_index)
df_right.index.name = "subid"
df_full = pd.DataFrame(all_full_data, index=subject_index)
df_full.index.name = "subid"

df_left.to_csv(data_dir / "left_volumes_thalamus.csv")
df_right.to_csv(data_dir / "right_volumes_thalamus.csv")
df_full.to_csv(data_dir / "full_volumes_thalamus.csv")
