# %%
from pathlib import Path
import pandas as pd
import csv
from tqdm import tqdm
from datetime import datetime
from loguru import logger
import re
import os
from statistics import mean
from helpers import fslstats
from tqdm import tqdm
# %%
dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
subject_sessions = pd.read_csv("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
data_dir = Path("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline") / "data0"


KEY_REF = [
    "6_VLPd.nii.gz",
    "6_VLPv.nii.gz",
    "15-CL.nii.gz",
    "thomas_anterior.nii.gz",
    "thomas_ventral.nii.gz",
    "thomas_medial.nii.gz",
    "thomas_posterior.nii.gz",
]


def parse_hipsthomas_vols(file):
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=" ")
        vols = {row[0]: float(row[1]) for row in reader}
    return vols


def get_extra_vols(loc_side):
    vols = parse_hipsthomas_vols(os.path.join(loc_side, "nucleiVols.txt"))
    for key in KEY_REF:
        mask  = os.path.join(loc_side, key)
        try:
            vols[key] = fslstats(mask, "-V")[0][1]
        except IndexError:
            print(fslstats(mask, "-V"))
            print(mask)
            raise
    
    with open(os.path.join(loc_side,"nucleiVolsSRS.txt"), 'w') as f:
        for key, val in vols.items():
            f.write(f"{key} {val}\n")
    return vols

def get_hipsthomas_vols(loc):
    left_vol_file = os.path.join(loc, "left", "nucleiVolsSRS.txt")
    if not os.path.exists(left_vol_file):
        left_vols = get_extra_vols(os.path.join(loc, "left"))
    else:
        left_vols = parse_hipsthomas_vols(left_vol_file)

    right_vol_file = os.path.join(loc, "left", "nucleiVolsSRS.txt")
    if not os.path.exists(right_vol_file):
        right_vols = get_extra_vols(os.path.join(loc, "right"))
    else:
        right_vols = parse_hipsthomas_vols(right_vol_file)


    # vols = {key: left_vols[key] + right_vols[key] for key in left_vols}
    return left_vols, right_vols


def rename_struct(struct):
    new_key = re.sub(r"(\d+)-([\w-]+)", r"\2_\1", struct)
    new_key = re.sub("-", "_", new_key)
    return new_key

# %%
all_left_data = []
all_right_data = []
all_full_data = []
continue_subject = False
subject_index = []

left_rows = []
right_rows = []
full_rows = []

for subid, sessions in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    subject = f"sub{subid}"
    subject_root = dataroot / subject / "group"
    csv_names = [f"sub{subid}_thomas_left_deformations.csv", 
                 f"sub{subid}_thomas_right_deformations.csv",
                 f"sub{subid}_thomas_bilateral_deformations.csv"]

    csv_paths = [subject_root / name for name in csv_names]
    try:
        left_vols, right_vols = get_hipsthomas_vols(subject_root)
    except Exception:
        print(f"Error collecting volumes for {subid}")
        continue
    full_vols = {key: left_vols[key]+right_vols[key] for key in left_vols}

    for path, rows, vols in zip(csv_paths, [left_rows, right_rows, full_rows], [left_vols, right_vols, full_vols]):
        # Load CSV
        if path.exists():
            df = pd.read_csv(path)
        else:
            print(subid)
            continue
        # Create time-specific column names
        df_time1 = df.set_index("struct")["ses1"].drop("4567-VL")
        df_time2 = df.set_index("struct")["ses2"].drop("4567-VL")
        df_vols = pd.Series(left_vols.values(), index=left_vols.keys())
        # Rename columns
        df_time1.index = [f"{rename_struct(struct)}_time1" for struct in df_time1.index]
        df_time2.index = [f"{rename_struct(struct)}_time2" for struct in df_time2.index]
        df_vols.index = [f"{rename_struct(struct)}_vol" for struct in df_vols.index]

        s_time = pd.Series({"time1": int(sessions['ses1']), "time2": int(sessions['ses2'])})

        # Combine time1 and time2 into one row
        combined = pd.concat([s_time, df_vols, df_time1, df_time2], axis=0)
        
        # Convert to single-row DataFrame
        combined_df = combined.to_frame().T
        
        # Assign subject ID as index
        combined_df.index = [subid]
        
        rows.append(combined_df)

# Concatenate all subjects
final_df = pd.concat(rows)

# Ensure subjectID is index name
final_df.index.name = "subid"

rename_keys = {}
for key in final_df:
    new_key = re.sub(r"(\d+)-([\w-]+)", r"\2_\1", key)
    new_key = re.sub("-", "_", new_key)
    rename_keys[key] = new_key
final_df = final_df.rename(columns=rename_keys)

# %%

final_df.to_csv("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/data0/deformation_data.csv")