import os
from pathlib import Path
import subprocess
from loguru import logger
import re
import shutil
import sys
from tqdm import tqdm

# Custom sink that uses tqdm.write
class TqdmLoguruStream:
    def write(self, message):
        tqdm.write(message, end='')
    
    def flush(self):
        pass


dataroot = Path("/media/smbshare/srs-9/IXI_dataset/HH")

logger.remove()  # Remove the default handler
logger.add(TqdmLoguruStream(), level="INFO")  # Add a new handler with WARNING level
logger.add((dataroot / "processing.log"), level="DEBUG")

fastsurfer_script = "/home/srs-9/Projects/ms_mri/scripts/fastsurfer/fastsurfer.sh"
hipsthomas_script = "/home/srs-9/Projects/ms_mri/scripts/hips_thomas.sh"

# mri_scans = [item for item in os.scandir(dataroot) if item.is_file()]

# for scan in mri_scans:
#     filepath = scan.path
#     filename = scan.name
#     subid = re.search(r".+(\d{4}).+\.nii\.gz", filename)[1]
#     subject_folder = dataroot / subid
#     if not os.path.exists(subject_folder):
#         os.makedirs(subject_folder)
#     dst = subject_folder / "t1.nii.gz"
#     shutil.copyfile(filepath, dst)

fastsurfer_root = dataroot / "fastsurfer"
subject_folders = [item.path for item in os.scandir(dataroot) if item.is_dir() and re.match(r"\d{4}", item.name)]

# with open("check.txt", 'w') as f:
for i, subject_root in tqdm(enumerate(subject_folders), total=len(subject_folders)):
    logger.debug(f"Next iteration; {i/len(subject_folders)*100}% done")
    subject_root = Path(subject_root)
    subid = subject_root.name
    if not (fastsurfer_root / subid).exists():
        fastsurfer_cmd = ["bash", fastsurfer_script, subid, str(dataroot), str(fastsurfer_root)]
        logger.info(" ".join(fastsurfer_cmd))
        try:
            result = subprocess.run(fastsurfer_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(e.stderr)
    
    if not (subject_root / "left/thomasfull_L.nii.gz").exists():
        hipsthomas_cmd = ["bash", hipsthomas_script, str(subject_root)]
        logger.info(" ".join(hipsthomas_cmd))
        try:
            result = subprocess.run(hipsthomas_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(e.stderr)

