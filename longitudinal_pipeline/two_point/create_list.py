# %%
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

# %%
subject_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")

lines = []
for subid in subject_sessions.index:
    subject_root = dataroot / f"sub{subid}"
    ses1 = str(int(subject_sessions.loc[subid, 'ses1']))
    ses2 = str(int(subject_sessions.loc[subid, 'ses2']))
    line = [str(subject_root), str(subid), ses1, ses2]
    lines.append(" ".join(line))


with open("param_list.txt", 'w') as f:
    for line in lines:
        f.write(line+"\n")