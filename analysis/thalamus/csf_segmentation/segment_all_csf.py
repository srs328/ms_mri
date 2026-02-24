from pathlib import Path
import os
import subprocess
import csv
from loguru import logger
import sys
from tqdm import tqdm
import pandas as pd


curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)

logger.remove()  # Remove the default handler
logger.add(sys.stderr, level="INFO")  # Add a new handler with WARNING level
logger.add(os.path.join(curr_dir, "segment.log"), level="DEBUG")

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")
subses_file = "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions-updated.csv"
segment_csf_script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/csf_segmentation/segment_csf.sh"



with open(subses_file, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    subject_sessions = [(sub, ses) for sub, ses in reader]

subject_sessions = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions-updated.csv",
    index_col="sub"
)

subjects = [2120, 2001,1394,1364,2106]
# for sub, ses in tqdm(subject_sessions):
for sub in subjects:
    print(sub)
    ses = subject_sessions.loc[sub, 'ses']
    subject_root = dataroot / f"sub{sub}-{ses}"
    if (subject_root / "peripheral_CSF_CHECK.nii.gz").exists():
        pass
        # logger.debug(f"CSF already segmented for sub{sub}-{ses}, skipping.")
        # continue
    cmd = ["bash", segment_csf_script, str(subject_root)]
    try:
        logger.info(" ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        logger.debug(e.stderr)
    else:
        logger.debug(result.stdout.decode('utf-8'))