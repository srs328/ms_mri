# %%
import shutil
import os
from pathlib import Path
import csv
from loguru import logger
from tqdm import tqdm

# %%
# Custom sink that uses tqdm.write
class TqdmLoguruStream:
    def write(self, message):
        tqdm.write(message, end='')
    
    def flush(self):
        pass

logger.remove()  # Remove the default handler
logger.add(TqdmLoguruStream(), level="INFO", format="{level} | {message}")

# %%
drive_root = Path("/mnt/h")
pioneer_bids_root = drive_root / "3Tpioneer_bids"
dataroot = drive_root / "srs-9/thalamus_project/data"

datafile_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")
with open(datafile_dir / "lst_ai-sessions.csv", 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    subject_sessions = list(reader)

# %%
for subid, sesid in tqdm(subject_sessions):
    pioneer_subject_root = pioneer_bids_root / f"sub-ms{subid}" / f"ses-{sesid}"
    subject_root = dataroot / f"sub{subid}-{sesid}"
    src = pioneer_subject_root / "lst-ai"
    dst = subject_root / "lst-ai"
    logger.info(f"Copying {src} to {dst}")
    shutil.copytree(src, dst, dirs_exist_ok=True)
