from pathlib import Path
import json
import os
import shutil
import subprocess

work_home = Path("/media/smbshare/srs-9/fastsurfer")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [str(subid) for subid in subjects]

fastsurfer_script = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/fastsurfer.sh"

logfile = "fastsurfer.log"

for subid in subjects:
    with open(logfile, 'a') as f:
        f.write(f"{subid}\n")

        sessions = sorted(subject_sessions[subid])
        sesid = sessions[0]

        subj_folder = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"
        
        # create work_dir if it doesn't exist
        output_folder = (work_home / f"sub{subid}-{sesid}")
        if not output_folder.exists():
            os.makedirs(output_folder)

        cmd = ["bash", fastsurfer_script, str(subid), subj_folder, output_folder]
        cmd_str = " ".join([str(item) for item in cmd])
        f.write(cmd_str + "\n")
        subprocess.run(cmd)