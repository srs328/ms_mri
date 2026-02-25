#%%
from pathlib import Path
import pandas as pd
import csv
from tqdm import tqdm
from datetime import datetime
from loguru import logger
import re
import os
from statistics import mean


# %%

now = datetime.now()
log_filename = now.strftime(
    f"{os.path.basename(__file__).split('.')[0]}-%Y%m%d_T%H%M%S.log"
)
logger.remove()
logger.add(log_filename, mode="w")

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


# %%
for subid, row in subject_sessions.iterrows():
    subject = f"sub{subid}"
    subject_root = dataroot / subject
    ses1, ses2 = int(row['ses1']), int(row['ses2'])

    ses1_folder = subject_root / str(ses1)
    left_file = ses1_folder / "left/nucleiVols.txt"
    right_file = ses1_folder / "right/nucleiVols.txt"
    if not left_file.exists() or not right_file.exists():
        print(f"No results for sub{subid} ses{ses1}")

    ses2_folder = subject_root / str(ses2)
    left_file = ses2_folder / "left/nucleiVols.txt"
    right_file = ses2_folder / "right/nucleiVols.txt"
    if not left_file.exists() or not right_file.exists():
        print(f"No results for sub{subid} ses{ses2}")


# %%

key_ref = [
    "1-THALAMUS",
    "2-AV",
    "4-VA",
    "5-VLa",
    "6-VLP",
    "7-VPL",
    "8-Pul",
    "9-LGN",
    "10-MGN",
    "11-CM",
    "12-MD-Pf",
    "13-Hb",
    "14-MTT",
    "26-Acc",
    "27-Cau",
    "28-Cla",
    "29-GPe",
    "30-GPi",
    "31-Put",
    "32-RN",
    "33-GP",
    "34-Amy",
]

all_left_data = []
all_right_data = []
all_full_data = []
continue_subject = False
subject_index = []
for subid, row in subject_sessions.iterrows():
    subject = f"sub{subid}"
    subject_root = dataroot / subject
    ses1, ses2 = str(int(row['ses1'])), str(int(row['ses2']))

    left_data = {}
    right_data = {}
    full_data = {}

    ses_num = 1
    for ses in [ses1, ses2]:
        ses_root = subject_root / str(ses)
        if (
            not (ses_root / "left" / "nucleiVols.txt").exists()
            or not (ses_root / "right" / "nucleiVols.txt").exists()
        ):
            continue

        left_data[f"time{ses_num}"] = right_data[f"time{ses_num}"] = full_data[
            f"time{ses_num}"
        ] = ses

        # Handle some errors
        try:
            left_vols, right_vols = get_hipsthomas_vols(ses_root)
        except Exception as e:
            logger.warning(f"Missing something for {subject} in session {ses}")
            logger.error(e)
            continue_subject = True
            break
        try:
            assert list(left_vols.keys()) == key_ref
        except AssertionError as e:
            logger.warning(f"Issue with {subject} in session {ses}, left side")
            logger.error(e)
            continue_subject = True
            break
        try:
            assert list(right_vols.keys()) == key_ref
        except AssertionError as e:
            logger.warning(f"Issue with {subject} in session {ses}, right side")
            logger.error(e)
            continue_subject = True
            break


        for key in left_vols:
            new_key = re.sub(r"(\d+)-([\w-]+)", r"\2_\1", key)
            new_key = re.sub("-", "_", new_key) + f"_time{ses_num}"
            left_data[new_key] = left_vols[key]
            right_data[new_key] = right_vols[key]
            full_data[new_key] = mean([right_vols[key], left_vols[key]])

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

df_left.to_csv(data_dir / "left_volumes.csv")
df_right.to_csv(data_dir / "right_volumes.csv")
df_full.to_csv(data_dir / "full_volumes.csv")

