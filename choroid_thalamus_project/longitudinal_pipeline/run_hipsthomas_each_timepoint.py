#%%
from pathlib import Path
import json
import os
import shutil
import subprocess
from mri_data import file_manager as fm
import re
from loguru import logger
from tqdm import tqdm

#%%
drive_root = fm.get_drive_root()
work_home = drive_root / "srs-9/longitudinal"
dataroot = drive_root / "3Tpioneer_bids"

work_home = Path("/media/smbshare/srs-9/longitudinal")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)


subjects = [item.name for item in os.scandir(work_home) if item.is_dir()]
subjects.sort()
with open("/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/subjects_to_process.txt", 'r') as f:
    subids = [line.strip() for line in f.readlines()]

hipsthomas_script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/runHipsThomas.sh"

logger.remove()
logger.add("run_hipsthomas.log", mode='w')

#%%

# for subject in tqdm(subjects, total=len(subjects)):
for subid in tqdm(subids, total=len(subids)):
    subject = f"sub{subid}"
    work_dir = work_home / subject

    # subid = re.search(r"sub(\d{4})", subject)[1]
    sessions = sorted(subject_sessions[subid])

    ses1 = sessions[0]
    ses1_dir = work_dir / str(ses1)
    if not ses1_dir.exists():
        os.makedirs(ses1_dir)
    if not (ses1_dir / "left").exists():
        scan1 = list(work_dir.glob(f"{subject}_input0000*_mniWarped-WarpedToTemplate.nii.gz"))[0]
        scan1_dst = ses1_dir / "t1.nii.gz"
        if not scan1_dst.exists():
            shutil.copyfile(scan1, scan1_dst)
        cmd = ["bash", hipsthomas_script, str(ses1_dir), scan1_dst.name]
        logger.info(f"Starting session {ses1} for subject {subid}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed session {ses1} for subject {subid}")
            logger.error(e.stdout)


    ses2 = sessions[-1]
    ses2_dir = work_dir / str(ses2)
    if not ses2_dir.exists():
        os.makedirs(ses2_dir)
    if not (ses2_dir / "left").exists():
        scan2 = list(work_dir.glob(f"{subject}_input0001*_mniWarped-WarpedToTemplate.nii.gz"))[0]
        scan2_dst = ses2_dir / "t1.nii.gz"
        if not scan2_dst.exists():
            shutil.copyfile(scan2, scan2_dst)
        cmd = ["bash", hipsthomas_script, str(ses2_dir), scan2_dst.name]
        logger.info(f"Starting session {ses2} for subject {subid}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(e.stderr)
            logger.error(f"Failed session {ses2} for subject {subid}")
            logger.error(e.stdout)

# %%
