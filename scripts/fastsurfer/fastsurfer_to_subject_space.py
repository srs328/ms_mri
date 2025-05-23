from pathlib import Path
import json
import os
import shutil
import subprocess
from tqdm import tqdm

work_home = Path("/media/smbshare/srs-9/fastsurfer")
dataroot = Path("/media/smbshare/3Tpioneer_bids")


with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

# subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [str(subid) for subid in subjects]

fastsurfer_script = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/fastsurfer_to_subject_space.sh"

for subid in tqdm(subjects, total=len(subjects)):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    subject_folder = (work_home / f"sub{subid}-{sesid}")
    cmd = ["bash", fastsurfer_script, subject_folder, str(subid)]
    subprocess.run(cmd)