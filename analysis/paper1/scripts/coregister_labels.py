import os
from pathlib import Path
import pandas as pd
import subprocess
from tqdm import tqdm

from mri_data import file_manager as fm
import logging
from datetime import datetime

drive_root = fm.get_drive_root()
labelroot = drive_root / "srs-9/paper1/labels"
dataroot = drive_root / "3Tpioneer_bids"

t1_label = "t1_choroid_pineal_pituitary_T1-1_pred.nii.gz"
flair_label = "flair_choroid_pineal_pituitary_FLAIR-1_pred.nii.gz"

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv")

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


def extract_labels(label, out_dir):
    choroid_cmd = f"fslmaths {label} -uthr 1 {out_dir}/choroid.nii.gz"
    subprocess.run(choroid_cmd.split(" "))

    pineal_cmd = f"fslmaths {label} -uthr 2 -thr 2 {out_dir}/pineal.nii.gz"
    subprocess.run(pineal_cmd.split(" "))

    pituitary_cmd = f"fslmaths {label} -thr 3 {out_dir}/pituitary.nii.gz"
    subprocess.run(pituitary_cmd.split(" "))


def extract_label(in_label, out_label, thr):
    cmd = f"fslmaths {in_label} {thr} {out_label}"
    subprocess.run(cmd.split(" "))


def subtract_labelmaps(label1, label2, out):
    cmd = f"fslmaths {label1} -sub {label2} {out}"
    subprocess.run(cmd.split(" "))


# flirt interpolates the labelmap but looks good otherwise,
# need to find another way
#   mri_vol2vol results don't look good
def register_label0(struct, loc, ref, aff):
    label = f"{loc}/{struct}.nii.gz"
    out = f"{loc}/{struct}-mni_reg.nii.gz"
    cmd = f"flirt -noresample -in {label} -ref {ref} -applyxfm -init {aff} -out {out}"
    subprocess.run(cmd.split(" "))


def register_label(in_label, ref, aff, out_label):
    cmd = f"flirt -noresample -in {in_label} -ref {ref} -applyxfm -init {aff} -out {out_label}"
    subprocess.run(cmd.split(" "))


# fix for flirt till I find a better way
def fix_label0(struct, loc):
    idx = {"choroid": 1, "pineal": 2, "pituitary": 3}
    label = f"{loc}/{struct}-mni_reg.nii.gz"
    out = f"{loc}/{struct}-mni_reg2.nii.gz"
    cmd = f"fslmaths {label} -thr 0.5 -div {label} -mul {idx[struct]} {out}"
    subprocess.run(cmd.split(" "))


def fix_label(label, out, idx):
    cmd = f"fslmaths {label} -thr 0.5 -div {label} -mul {idx} {out}"
    subprocess.run(cmd.split(" "))


for i, row in tqdm(df.iterrows(), total=len(df)):
    label_t1 = drive_root / row.label_folder / t1_label
    if not label_t1.is_file():
        continue
    label_flair = drive_root / row.label_folder / flair_label
    if not label_flair.is_file():
        continue

    if not (labelroot / row["sub-ses"]).is_dir():
        os.makedirs(labelroot / row["sub-ses"])

    choroid_t1 = labelroot / row["sub-ses"] / "t1-choroid.nii.gz"
    choroid_flair = labelroot / row["sub-ses"] / "flair-choroid.nii.gz"

    if not choroid_t1.is_file():
        extract_label(label_t1, choroid_t1, "-uthr 1")
    if not choroid_flair.is_file():
        extract_label(label_flair, choroid_flair, "-uthr 1")

    choroid_diff = labelroot / row["sub-ses"] / "t1_flair_diff-choroid.nii.gz"
    subtract_labelmaps(choroid_t1, choroid_flair, choroid_diff)

    aff = dataroot / row["sub-ses"] / "proc/t1_std.mat"
    ref = dataroot / row["sub-ses"] / "proc/t1_std.nii.gz"
    if not ref.is_file():
        continue

    choroid_t1_reg = labelroot / row["sub-ses"] / "t1-choroid-std.nii.gz"
    if not choroid_t1_reg.is_file():
        register_label(choroid_t1, ref, aff, choroid_t1_reg)

    choroid_t1_reg2 = labelroot / row["sub-ses"] / "t1-choroid-std2.nii.gz"
    if not choroid_t1_reg2.is_file():
        fix_label(choroid_t1_reg, choroid_t1_reg2, 1)

    choroid_flair_reg = labelroot / row["sub-ses"] / "flair-choroid-std.nii.gz"
    if not choroid_flair_reg.is_file():
        register_label(choroid_flair, ref, aff, choroid_flair_reg)

    choroid_flair_reg2 = labelroot / row["sub-ses"] / "flair-choroid-std2.nii.gz"
    if not choroid_flair_reg2.is_file():
        fix_label(choroid_flair_reg, choroid_flair_reg2, 1)

    choroid_diff_reg = labelroot / row["sub-ses"] / "t1_flair_diff-choroid-std.nii.gz"
    if not choroid_diff_reg.is_file():
        logger.info(row["subid"])
        subtract_labelmaps(choroid_t1_reg2, choroid_flair_reg2, choroid_diff_reg)


# for i, row in df.iloc[:2].iterrows():
#     label_t1 = drive_root / row.label_folder / row.label
#     out_dir = label_root / row["sub-ses"]
#     if not out_dir.is_dir():
#         os.makedirs(out_dir)
#     extract_labels(label_t1, out_dir)

#     label_flair = drive_root / row.label_folder / flair_label
#     extract_labels(label_flair, out_dir)

#     aff = dataroot / row["sub-ses"] / "proc/t1_std.mat"
#     ref = dataroot / row["sub-ses"] / "proc/t1_std.nii.gz"
#     for struct in ["choroid", "pineal", "pituitary"]:
#         out = out_dir / f"{struct}_std.nii.gz"
#         # if not out.is_file():
#         register_label(struct, out_dir, ref, aff)
#         fix_label(struct, out_dir)
