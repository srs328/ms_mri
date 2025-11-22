import os
from pathlib import Path
import shutil
import subprocess
import csv
from tqdm import tqdm
from loguru import logger

class TqdmLoguruStream:
    def write(self, message):
        tqdm.write(message, end='')
    
    def flush(self):
        pass

logger.remove()  # Remove the default handler
logger.add(TqdmLoguruStream(), level="INFO", format="{level} | {message}")


dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
output_root = Path("/mnt/i/Data/srs-9/fsl_first")

script = "run_first.sh"

datafile_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")
with open(datafile_dir / "lst_ai-sessions.csv", 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    subject_sessions = list(reader)


for subid, sesid in tqdm(subject_sessions, desc="Running FSL first", unit="subject"):
    logger.info(f"Starting sub{subid}-{sesid}")
    subject_root1 = dataroot / f"sub{subid}-{sesid}"
    subject_root2 = output_root / f"sub{subid}-{sesid}"
    if not subject_root2.exists():
        logger.info(f"Creating folder {str(subject_root2)}")
        os.makedirs(subject_root2)

    if not (subject_root2 / "t1.nii.gz").exists():
        logger.info(f"Copying t1.nii.gz into {str(subject_root2)}")
        # shutil.copy(subject_root1/"t1.nii.gz", subject_root2/"t1.nii.gz")
        subprocess.run(["cp", str(subject_root1/"t1.nii.gz"), str(subject_root2/"t1.nii.gz")])

    if (subject_root2 / "t1-L_Thal_first.nii.gz").exists():
        logger.info(f"{str(subject_root2 / "t1-L_Thal_first.nii.gz")} already exists")
        continue
    
    # run_first_all -dv -i t1.nii.gz -o t1
    cmd = ["bash", "run_first.sh", str(subject_root2)]
    try:
        logger.info(f"{" ".join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)