import os
import pandas as pd
import subprocess
from tqdm import tqdm

from mri_data import file_manager as fm
import logging
from datetime import datetime

drive_root = fm.get_drive_root()
labelroot = drive_root / "srs-9/paper1/labels"
dataroot = drive_root / "3Tpioneer_bids"

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv", index_col="subid")

logdir = "/home/srs-9/Projects/ms_mri/analysis/paper1/scripts/logs"
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


def register_volume(in_vol, ref, aff, out_vol):
    cmd = f"flirt -noresample -in {in_vol} -ref {ref} -applyxfm -init {aff} -out {out_vol}"
    subprocess.run(cmd.split(" "))


reg_subs = [
    1548,
    1487,
    1328,
    1544,
    1487,
    1442,
    1066,
    1453,
    1248,
    1117,
    1001,
    1237,
    1158,
    1272,
    1518,
    1246,
    2027
]

work_df = df.loc[reg_subs, :]

for i, row in tqdm(work_df.iterrows(), total=len(work_df)):
    aff = dataroot / row["sub-ses"] / "proc/t1_std.mat"
    ref = dataroot / row["sub-ses"] / "proc/t1_std.nii.gz"
    if not ref.is_file():
        continue

    flair = dataroot / row["sub-ses"] / "flair.nii.gz"
    flair_std = dataroot / row["sub-ses"] / "proc/flair_std.nii.gz"
    if flair.is_file() and not flair_std.is_file():
        register_volume(flair, ref, aff, flair_std)

    t1_gd = dataroot / row["sub-ses"] / "t1_gd.nii.gz"
    t1_gd_std = dataroot / row["sub-ses"] / "proc/t1_gd_std.nii.gz"
    if t1_gd.is_file() and not t1_gd_std.is_file():
        register_volume(t1_gd, ref, aff, t1_gd_std)