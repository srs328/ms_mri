from pathlib import Path
import json
import os
import shutil
import subprocess
from loguru import logger
import sys

curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)

logger.remove()  # Remove the default handler
logger.add(sys.stderr, level="INFO")  # Add a new handler with WARNING level
logger.add(os.path.join(curr_dir, "run_lst_ai.log"), level="DEBUG")


# work_home = Path("/media/smbshare/srs-9/fastsurfer")
# dataroot = Path("/media/smbshare/3Tpioneer_bids")
dataroot = Path("/mnt/h/3Tpioneer_bids")


with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

# with open("/home/srs-9/Projects/ms_mri/scripts/lst-ai/ms_patients.txt", 'r') as f:
with open("/home/srs-9/Projects/ms_mri/scripts/lst-ai/subjects_to_process2.txt", 'r') as f:
    subjects = [line.strip() for line in f.readlines()]

lstai_script = "/home/srs-9/Projects/ms_mri/scripts/lst-ai/lst_ai.sh"

subjects_to_process = []
subjects_processed = []
# for subid in subject_sessions:
for subid in subjects:
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    work_dir = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"

    cmd = ["bash", lstai_script, str(work_dir)]
    cmd_str = " ".join([str(item) for item in cmd])
    # f.write(cmd_str + "\n")
    # subprocess.run(cmd)
    check_dir = work_dir / "lst-ai"
    if (check_dir / "annotated_lesion_stats.csv").exists():
        subjects_processed.append(subid)
    else:
        subjects_to_process.append(subid)

print("Number of subjects to process: ", len(subjects_to_process))
print("Number of subjects processed: ", len(subjects_processed))

with open(os.path.join(curr_dir, "subjects_to_process3.txt"), 'w') as f:
    for subid in subjects_to_process:
        f.write(subid + "\n")