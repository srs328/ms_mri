import os
from pathlib import Path
import pandas as pd
import subprocess
import logging
from datetime import datetime

from mri_data import file_manager as fm

logdir = "/home/srs-9/Projects/ms_mri/mri_preproc/logs"
now = datetime.now()
curr_time = now.isoformat(timespec="hours")
filename = os.path.join(logdir, f"{curr_time} processing.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(filename)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


drive_root = fm.get_drive_root()
label_root = drive_root / "srs-9/paper1/labels"
dataroot = drive_root / "3Tpioneer_bids"

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv")

processing_script = "/home/srs-9/Projects/ms_mri/scripts/register_scans.sh"

for i, row in df.iloc[:2].iterrows():
    scan_dir = dataroot / row["sub-ses"]
    modality = "t1"
    command_parts = [processing_script, str(scan_dir), modality, "1"]
    try:
        logger.info(" ".join(command_parts))
        result = subprocess.run(
            command_parts, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logger.info(e.stdout)
        logger.error(e.stderr)
    else:
        logger.debug(result.stdout)
