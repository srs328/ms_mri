import pandas as pd
from loguru import logger
from pathlib import Path
from tqdm import tqdm
import os
import re
import sys
import shutil

import subprocess

from mri_data.file_manager import scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

drive_root = fm.get_drive_root()
msmri_home = Path("/home/srs-9/Projects/ms_mri")
inference_root = drive_root / "srs-9" / "3Tpioneer_bids_predictions"
dataroot = drive_root / "3Tpioneer_bids"
clinical_data_root = drive_root / "Secure_Data" / "Large"
data_file_folder = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/data0")


hipsthomas_home = Path("/media/smbshare/srs-9/thalamus_seg/hipsthomas_out")

dataset_proc = DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)

dataset = dataset_proc.dataset
dataset.sort()


for scan in tqdm(dataset[2:]):
    try:
        if not (scan.root / "t1.nii.gz").exists():
            continue

        subject_folder = hipsthomas_home / f"sub{scan.subid}-{scan.sesid}"
        # if (subject_folder / "crop_t1.nii.gz").exists():
        #     continue

        if not subject_folder.exists():
            os.makedirs(subject_folder)

        if not (subject_folder / "t1.nii.gz").exists():     
            shutil.copyfile(scan.root / "t1.nii.gz", subject_folder / "t1.nii.gz")

        print(scan.subid)
        cmd = ["bash", "/home/srs-9/Projects/ms_mri/scripts/hips_thomas.sh", str(subject_folder)]
        subprocess.run(cmd)
    except Exception:
        continue

