from pathlib import Path
import json
import os
import shutil
import subprocess
from tqdm import tqdm

fastsurfer_home = Path("/media/smbshare/srs-9/fastsurfer")
hipsthomas_home = Path("/media/smbshare/srs-9/thalamus_project/data")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

# subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [str(subid) for subid in subjects]

fastsurfer_to_subject_space = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/fastsurfer_to_subject_space.sh"
script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/scripts/processAseg.sh"

# for subid in subjects:
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    fastsurfer_dir = fastsurfer_home / f"sub{subid}-{sesid}" / subid
    print(fastsurfer_dir)

    if not (fastsurfer_dir / "mri").exists():
        continue
    if not (fastsurfer_dir / "mri" / "freesurfer-to-subject.mat").exists():
        cmd = ["bash", fastsurfer_to_subject_space, fastsurfer_dir.parent, str(subid)]
        subprocess.run(cmd)

    hipsthomas_dir = hipsthomas_home / f"sub{subid}-{sesid}"

    cmd = ["bash", script, fastsurfer_dir, hipsthomas_dir]
    print(" ".join([str(item) for item in cmd]))
    subprocess.run(cmd)