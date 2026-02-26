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
min_time = 1 #year
max_time = 6

all_sessions = {}
for sub in df_base.index:
    # print(sub)
    ses1 = subject_sessions.loc[sub, 'ses']
    ses_list = subject_sessions_longit[str(sub)]
    if len(ses_list) < 2:
        continue
    sessions = [int(ses1)]
    for ses in ses_list:
        if get_diff(ses, ses1) >= min_time*365 and get_diff(ses, ses1) <= max_time*365:
            sessions.append(ses)
    if len(sessions) < 2:
        continue
    all_sessions[sub] = sessions
    
with open("all_longitudinal_sessions.json", 'w') as f:
    json.dump(all_sessions, f, indent=4)

# %%
long_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
new_sessions = []
for subid in all_sessions:
    finished_sessions = []
    try:
        prev_sessions =  [int(long_sessions.loc[subid, 'ses1']), int(long_sessions.loc[subid, 'ses2'])]
    except KeyError:
        prev_sessions = []
    for ses in all_sessions[subid]:
        if ses not in prev_sessions:
            new_sessions.append((subid, ses))

df_sessions = pd.DataFrame(new_sessions, columns=["subid", "sesid"]).set_index("subid")
df_sessions.to_csv("longitudinal_sessions2.csv")

# pick_sessions = [session for session in sessions 
#                  if session[3] > 3]

# test = pd.DataFrame(pick_sessions, columns=["subid", "ses1", "ses2", "t_diff"]).set_index("subid")
# test.to_csv("longitudinal_sessions.csv")


# %%
dataroot = Path("/mnt/h/3Tpioneer_bids")
target_root = Path("/mnt/i/Data/longitudinal")

for subid, sesid in tqdm(df_sessions.iterrows(), total=len(df_sessions)):
    ses1 = str(sesid["sesid"])
    subroot = dataroot / f"sub-ms{subid}"
    ses1_root = subroot / f"ses-{ses1}"

    t1_ses1 = ses1_root / "t1.nii.gz"

    if not t1_ses1.exists():
        continue

    target_subroot = target_root / f"sub{subid}"
    target_ses1_dir = target_subroot / str(ses1)
    if (target_ses1_dir/"t1.nii.gz").exists():
        continue

    os.makedirs(target_subroot, exist_ok=True)
    os.makedirs(target_ses1_dir, exist_ok=True)
    
    shutil.copyfile(t1_ses1, target_ses1_dir/"t1.nii.gz")
    
# %%

df_sessions = pd.read_csv("longitudinal_sessions2.csv", index_col="subid")

paths = []
for subid, row in df_sessions.iterrows():
    sesid = str(row['sesid'])
    path = os.path.join("/home/shridhar.singh9-umw/data/longitudinal", f"sub{subid}", sesid)
    paths.append(path + "\n")
    
with open("subjects2.txt", 'w') as f:
    f.writelines(paths)