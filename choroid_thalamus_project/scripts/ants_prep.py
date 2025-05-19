from pathlib import Path
import os
import json
import shutil

work_home = Path("/home/srs-9/data_tmp/longitudinal")
dataroot = Path("/mnt/h/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

subjects = ['1161', '1107', '1326', '1527']

for subid in subjects:
    work_dir = (work_home / f"sub{subid}")
    if not work_dir.exists():
        os.makedirs(work_dir)

    sessions = subject_sessions[subid]
    for sesid in sessions:

        t1_path = dataroot / f"sub-ms{subid}" / f"ses-{sesid}" / "t1.nii.gz"
        save_path = work_dir / f"t1_{sesid}.nii.gz"
        shutil.copyfile(t1_path, save_path)

