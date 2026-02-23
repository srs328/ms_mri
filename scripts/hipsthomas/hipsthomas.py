from pathlib import Path
import json
import os
import shutil
import subprocess
import pandas as pd

# work_home = Path("/media/smbshare/srs-9/fastsurfer")
# dataroot = Path("/media/smbshare/3Tpioneer_bids")
work_home = Path("/mnt/h/srs-9/hipsthomas")
dataroot = Path("/mnt/h/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions_longit = json.load(f)

subject_sessions = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions-updated.csv",
    index_col="sub"
)

subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [str(subid) for subid in subjects]

hipsthomas_script = "/home/srs-9/Projects/ms_mri/scripts/hipsthomas/hipsthomas.sh"

logfile = "hipsthoms.log"

subjects = [2120, 2001,1394,1364,2106]

# for subid in subject_sessions_longit:
for subid in subjects:
    with open(logfile, 'a') as f:
        f.write(f"{subid}\n")

        # sessions = sorted(subject_sessions_longit[subid])
        # sesid = sessions[0]
        sesid = subject_sessions.loc[subid, 'ses']

        subj_folder = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"
        
        # create work_dir if it doesn't exist
        output_folder = (work_home / f"sub{subid}-{sesid}")
        if not output_folder.exists():
            os.makedirs(output_folder)
            shutil.copyfile(subj_folder/"t1.nii.gz", output_folder/"t1.nii.gz")
            f.write(f"Created {str(output_folder)} and copied T1\n")
        elif (output_folder/"sthomas_LR_labels").exists():
            continue

        cmd = ["bash", hipsthomas_script, output_folder]
        cmd_str = " ".join([str(item) for item in cmd])
        f.write(cmd_str + "\n")
        subprocess.run(cmd)