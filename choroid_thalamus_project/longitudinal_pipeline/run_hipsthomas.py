from pathlib import Path
import os
import json
import shutil
import subprocess

work_home = Path("/media/smbshare/srs-9/longitudinal")
dataroot = Path("/media/smbshare/3Tpioneer_bids")
work_home = Path("/mnt/h/srs-9/longitudinal")
dataroot = Path("/mnt/h/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

# 1225 failed ants
# 2195 already run
# subjects = ['1376', '2075', '1023', '1038', '1098']
subjects = ['1225']
script_path = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/scripts/runHipsThomas.sh"
logfile = "hipsthomas.log"

for subid in subjects:
    with open(logfile, 'a') as f:
        f.write(f"{subid}\n")
    
    work_dir = (work_home / f"sub{subid}")
    cmd = ["bash", script_path, subid, str(work_dir)]
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(e)
        continue