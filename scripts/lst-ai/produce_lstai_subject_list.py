from pathlib import Path
import json
import os
from loguru import logger
import sys
import csv

curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)

logger.remove()  # Remove the default handler
logger.add(sys.stderr, level="INFO")  # Add a new handler with WARNING level
logger.add(os.path.join(curr_dir, "run_lst_ai.log"), level="DEBUG")


dataroot = Path("/mnt/h/3Tpioneer_bids")
out_name = "lst_ai-sessions.csv"

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

with open("/home/srs-9/Projects/ms_mri/scripts/lst-ai/ms_patients.txt", 'r') as f:
    subjects = [line.strip() for line in f.readlines()]


def get_sesid(subid):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    work_dir = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"
    ses_ind = 1
    while not (work_dir / "lst-ai" / "lesion_stats.csv").exists():
        try:
            sesid = sessions[ses_ind]
        except IndexError:
            return None
        work_dir = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"
        ses_ind += 1
    return sesid


failed_subs = []
rows = []
for subid in subjects:
    sessions = sorted(subject_sessions[subid])
    sesid = get_sesid(subid)
    if sesid is None:
        logger.warning(f"sub{subid} does not have an lst-ai folder")
        failed_subs.append(subid)
        continue

    rows.append((int(subid), int(sesid)))
    
out_file = os.path.join(curr_dir, out_name)
with open(out_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['subid', 'sesid'])  # Header
    writer.writerows(rows)  # All data rows at once
