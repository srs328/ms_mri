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

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv")

df.loc[df["sub-ses"].isna(), "sub-ses"] = ""
df.loc[df["label_folder"].isna(), "label_folder"] = ""
df.loc[df["label"].isna(), "label"] = ""

has_labelfile = []
for i, row in df.iterrows():
    file = labelroot / row["sub-ses"] / "t1_flair_diff-choroid-std.nii.gz"
    if file.exists():
        has_labelfile.append(i)

w_contrast = df[(df.index.isin(has_labelfile)) & (df["flair_contrast"] == "WITH")]
wo_contrast = df[(df.index.isin(has_labelfile)) & (df["flair_contrast"] == "WITHOUT")]


def average_labelmaps(labelmaps, out):
    cmd_str = f"fslmaths {labelmaps[0]}"
    for lab in labelmaps[1:]:
        cmd_str = cmd_str + f" -add {lab}"
    cmd_str = cmd_str + f" -div {len(labelmaps)} {out}"
    subprocess.run(cmd_str.split(" "))


w_cont_labels = [
    labelroot / row["sub-ses"] / "t1_flair_diff-choroid-std.nii.gz"
    for i, row in w_contrast.iterrows()
]

out = labelroot / "with_contrast_test.nii.gz"
average_labelmaps(w_cont_labels, out)


wo_cont_labels = [
    labelroot / row["sub-ses"] / "t1_flair_diff-choroid-std.nii.gz"
    for i, row in wo_contrast.iterrows()
]

out = labelroot / "wo_contrast_test.nii.gz"
average_labelmaps(wo_cont_labels, out)
