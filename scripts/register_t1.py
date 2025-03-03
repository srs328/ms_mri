import pandas as pd
from pathlib import Path
from tqdm import tqdm
import os
import re
import subprocess
from datetime import datetime

from mri_data.file_manager import scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser
import logging


logdir = "/home/srs-9/Projects/ms_mri/scripts/logs"
now = datetime.now()
curr_time = now.isoformat(timespec="hours")
filename = os.path.join(logdir, f"{curr_time} processing.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(filename)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh)

drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"


dataset_proc = DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)
dataset = dataset_proc.dataset

for scan in tqdm(dataset, total=len(dataset)):
    t1 = scan.root / "t1.nii.gz"
    proc_dir = scan.root / "proc"

    if not proc_dir.is_dir():
        os.makedirs(proc_dir)

    if (proc_dir / "t1_std.nii.gz").is_file():
        continue

    cmd = f"first_flirt {scan.root}/t1 {proc_dir}/t1_std"
    try:
        logger.info(cmd)
        subprocess.run(cmd.split(" "), check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.info(f"Command failed with exit code {e.returncode}:")
        logger.error(e.stderr)
