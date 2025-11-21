from pathlib import Path
import json
import os
import shutil
import subprocess
from loguru import logger
import sys
from tqdm import tqdm

curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)

# Custom sink that uses tqdm.write
class TqdmLoguruStream:
    def write(self, message):
        tqdm.write(message, end='')
    
    def flush(self):
        pass

logger.remove()  # Remove the default handler
logger.add(TqdmLoguruStream(), level="INFO", format="{time:YYYY-MM-DD HH:MM:SS} | {level} | {message}")
# logger.add(sys.stderr, level="INFO")  # Add a new handler with WARNING level
logger.add(os.path.join(curr_dir, "run_lst_ai.log"), level="DEBUG")


# work_home = Path("/media/smbshare/srs-9/fastsurfer")
# dataroot = Path("/media/smbshare/3Tpioneer_bids")
dataroot = Path("/mnt/h/3Tpioneer_bids")

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

with open("/home/srs-9/Projects/ms_mri/scripts/lst-ai/subjects_to_process3.txt", 'r') as f:
    subjects = [line.strip() for line in f.readlines()]

lstai_script = "/home/srs-9/Projects/ms_mri/scripts/lst-ai/lst_ai.sh"

# for subid in subject_sessions:
for subid in tqdm(subjects, total=len(subjects), desc="Processing subjects", unit="subject"):
    logger.info(f"Starting subject {subid}")
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    work_dir = dataroot / f"sub-ms{subid}" / f"ses-{sesid}"

    cmd = ["bash", lstai_script, str(work_dir)]
    cmd_str = " ".join([str(item) for item in cmd])
    logger.info(cmd_str)
    try:    
        result = subprocess.run(cmd, text=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        tqdm.write(f"ERROR: {subid} failed")
        logger.error(e.stderr)
        continue
    else:
        logger.debug(result.stdout.decode('utf-8'))
    