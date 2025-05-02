# %%
from pathlib import Path
import shutil
import os
import csv
from tqdm import tqdm

# %%
hipsthomas_root = Path("/media/smbshare/srs-9/hipsthomas")
dataroot = Path("/media/smbshare/srs-9/thalamus_project/data")

with open("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv", 'r') as f:
    reader = csv.reader(f)
    subject_sessions = [line for line in reader]


# %%
for sub, ses in tqdm(subject_sessions):
    thomas_subdir = hipsthomas_root / f"sub{sub}-{ses}"
    data_subdir = dataroot / f"sub{sub}-{ses}"

    t1_src =  thomas_subdir / "t1.nii.gz"
    t1_dst = data_subdir / "t1.nii.gz"
    if not t1_dst.exists() and t1_src.exists():
        shutil.copyfile(t1_src, t1_dst)
    elif not t1_src.exists():
        print(f"No t1 for {sub}")

    sthomasL_src = thomas_subdir / "left" / "thomasfull_L.nii.gz"
    sthomasL_dst = data_subdir / "thomasfull_L.nii.gz"
    if not sthomasL_dst.exists() and sthomasL_src.exists():
        shutil.copyfile(sthomasL_src, sthomasL_dst)
    elif not sthomasL_src.exists():
        print(f"No thomasL for {sub}")

    sthomasR_src = thomas_subdir / "right" / "thomasfull_R.nii.gz"
    sthomasR_dst = data_subdir / "thomasfull_R.nii.gz"
    if not sthomasR_dst.exists() and sthomasR_src.exists():
        shutil.copyfile(sthomasR_src, sthomasR_dst)
    elif not sthomasR_src.exists():
        print(f"No thomasR for {sub}")
    
# %%
