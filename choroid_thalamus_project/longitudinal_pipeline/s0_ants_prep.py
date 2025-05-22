from pathlib import Path
import os
import json
import shutil

work_home = Path("/media/smbshare/srs-9/longitudinal")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

subjects = ['2195', '1225', '1376', '2075', '1023', '1038', '1098']

for subid in subjects:
    work_dir = (work_home / f"sub{subid}")
    if not work_dir.exists():
        os.makedirs(work_dir)

    sessions = subject_sessions[subid]
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    for sesid in sessions:
        t1_path = dataroot / f"sub-ms{subid}" / f"ses-{sesid}" / "t1.nii.gz"
        save_path = work_dir / f"t1_{sesid}.nii.gz"
        shutil.copyfile(t1_path, save_path)

# /home/srs-9/fsl/data/standard/MNI152_T1_1mm.nii.gz
