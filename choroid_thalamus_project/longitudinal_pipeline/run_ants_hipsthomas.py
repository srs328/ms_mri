from pathlib import Path
import json
import os
import shutil
import subprocess
from mri_data import file_manager as fm

drive_root = fm.get_drive_root()
work_home = drive_root / "srs-9/longitudinal"
dataroot = drive_root / "3Tpioneer_bids"

work_home = Path("/media/smbshare/srs-9/longitudinal")
dataroot = Path("/media/smbshare/3Tpioneer_bids")

with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)


subjects_file = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/candidates_to_process.txt"
with open(subjects_file, 'r') as f:
    subjects = [line.strip() for line in f.readlines() if len(line.strip()) > 0 and line[0] != "#"]

quick_register_script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/antsQuickRegister.sh"
template_script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/constructTemplate.sh"
hipsthomas_script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/runHipsThomas.sh"

logfile = "ants.log"

for subid in subjects:
    with open(logfile, 'a') as f:
        f.write(f"{subid}\n")
    
    # create work_dir if it doesn't exist
    work_dir = (work_home / f"sub{subid}")
    if not work_dir.exists():
        os.makedirs(work_dir)
    else:
        continue

    sessions = sorted(subject_sessions[subid])
    # just copy first and last to speed things up
    sessions = [sessions[0], sessions[-1]] 
    
    try:
        # copy t1 files to work_dir
        for sesid in sessions:
            t1_path = dataroot / f"sub-ms{subid}" / f"ses-{sesid}" / "t1.nii.gz"
            save_path = work_dir / f"t1_{sesid}.nii.gz"
            shutil.copyfile(t1_path, save_path)

        # run antsRegistrationSyNQuick to bring all scans into MNI space
        for sesid in sessions:
            cmd = ["bash", quick_register_script, str(sesid), str(work_dir)]
            subprocess.run(cmd)

        # run antsMultivariateTemplateConstruction2
        cmd = ["bash", template_script, subid, str(work_dir)]
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"sub{subid} failed, continuing")
            print(e)
            continue

        # run HIPS-THOMAS on the subject template
        cmd = ["bash", hipsthomas_script, subid, str(work_dir)]
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"sub{subid} failed, continuing")
            print(e)
            continue
    
    except Exception as e:
        print(f"sub{subid} failed, continuing")
        print(e)
