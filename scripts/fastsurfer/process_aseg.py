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
logger.add(os.path.join(curr_dir, "procAseg.log"), level="DEBUG")


work_home = Path("/mnt/h/srs-9/fastsurfer")
dataroot = Path("/mnt/h/srs-9/thalamus_project/data")


with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

# subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
subjects = [str(subid) for subid in subjects]

fastsurfer_script = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/processAseg.sh"

for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    fastsurfer_folder = (work_home / f"sub{subid}-{sesid}" / str(subid))
    save_folder = dataroot / f"sub{subid}-{sesid}"
    cmd = ["bash", fastsurfer_script, str(fastsurfer_folder), str(save_folder)]
    try:
        logger.info(" ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        logger.debug(e.stderr)
