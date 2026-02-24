# %%
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

subject_sessions = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions-updated.csv",
    index_col="sub"
)
df_base = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv", 
    index_col="subid")
df_base = df_base[df_base['dz_type2'] == "MS"]
with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions_longit = json.load(f)


def get_diff(ses2, ses1):
    return (datetime.strptime(str(ses2), "%Y%m%d") - datetime.strptime(str(ses1), "%Y%m%d")).days



# %%

sessions = []
for sub in df_base.index:
    # print(sub)
    ses1 = subject_sessions.loc[sub, 'ses']
    ses_list = subject_sessions_longit[str(sub)]
    if len(ses_list) < 2:
        continue
    ses2 = ses1
    t_diff = 0
    for ses in ses_list:
        if abs((new_diff := get_diff(ses, ses1)) - 5*365) < abs(get_diff(ses2, ses1) - 5*365):
            ses2 = ses
            t_diff = new_diff/365

        
    sessions.append((sub, str(ses1), str(ses2), t_diff))


pick_sessions = [session for session in sessions 
                 if session[3] > 3]

test = pd.DataFrame(pick_sessions, columns=["subid", "ses1", "ses2", "t_diff"]).set_index("subid")
test.to_csv("longitudinal_sessions.csv")


# %%
dataroot = Path("/mnt/h/3Tpioneer_bids")
target_root = Path("/mnt/h/srs-9/longitudinal")

for subid, sesids in tqdm(test.iterrows()):
    ses1 = str(sesids["ses1"])
    ses2 = str(sesids["ses2"])
    subroot = dataroot / f"sub-ms{subid}"
    ses1_root = subroot / f"ses-{ses1}"
    ses2_root = subroot / f"ses-{ses2}"

    t1_ses1 = ses1_root / "t1.nii.gz"
    t1_ses2 = ses2_root / "t1.nii.gz"

    if not t1_ses1.exists() or not t1_ses2.exists():
        continue

    target_subroot = target_root / f"sub{subid}"
    os.makedirs(target_subroot, exist_ok=True)
    target_ses1_dir = target_subroot / str(ses1)
    os.makedirs(target_ses1_dir, exist_ok=True)
    target_ses2_dir = target_subroot / str(ses2)
    os.makedirs(target_ses2_dir, exist_ok=True)
    
    shutil.copyfile(t1_ses1, target_ses1_dir/"t1.nii.gz")
    shutil.copyfile(t1_ses2, target_ses2_dir/"t1.nii.gz")