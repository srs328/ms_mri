# %%
import pandas as pd
from pathlib import Path
import os
import nibabel as nib
import numpy as np
from tqdm import tqdm
from mri_data import utils
import csv
import pandas as pd

data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

subject_sessions = pd.read_csv(data_file_dir / "subject-sessions.csv")

data = {"subid": [], "tiv": []}
for i, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    sub = row['sub']
    ses = row['ses']
    scan_root = dataroot / f"sub-ms{sub}" / f"ses-{ses}"

    try:
        tiv = utils.compute_volume(scan_root / "t1.mask.nii.gz")[1]
    except Exception as e:
        print(sub)
        tiv = None
        
    
    data['subid'].append(sub)
    data['tiv'].append(tiv)


df = pd.DataFrame(data)
df = df.set_index("subid")
df.index.name = "subid"
df.to_csv("tiv_data.csv")

#%%

