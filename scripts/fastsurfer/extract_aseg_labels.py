from pathlib import Path
import json
import os
import shutil
import subprocess
from tqdm import tqdm
from loguru import logger
import sys

curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)

logger.remove()  # Remove the default handler
logger.add(sys.stderr, level="INFO")  # Add a new handler with WARNING level
logger.add(os.path.join(curr_dir, "extractAsegLabels.log"), level="DEBUG")


dataroot = Path("/mnt/h/srs-9/thalamus_project/data")


with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

fastsurfer_script = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/extractAsegLabels.sh"

for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    work_dir = dataroot / f"sub{subid}-{sesid}"
    cmd = ["bash", fastsurfer_script, str(work_dir)]
    try:
        logger.info(" ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        logger.debug(e.stderr.decode('utf-8'))
    else:
        logger.debug(result.stdout.decode('utf-8'))
