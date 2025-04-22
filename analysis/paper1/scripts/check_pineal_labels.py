from pathlib import Path
import pandas as pd
import csv

from mri_data import file_manager as fm

drive_root = fm.get_drive_root()

dataroot = drive_root / "3Tpioneer_bids"

data_dir = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/data0")
df_full = pd.read_csv(data_dir / "t1_2_data_full.csv", index_col="subid")

out_rows = [["Subject", "pineal-SRS", "pineal-SRS_T1"]]
for sub, row in df_full.iterrows():
    if not isinstance(row['sub-ses'], str):
        continue
    sub_folder = dataroot / row['sub-ses']
    check_labels = ["pineal-SRS.nii.gz", "pineal-SRS_T1.nii.gz"]
    labels = ["" for i in check_labels]
    for i, lab in enumerate(check_labels):
        if (sub_folder / lab).exists():
            labels[i] = "Yes"

    if any(labels):
        out_rows.append([sub] + labels)

out_file = dataroot / "pineal_labels.csv"
if not out_file.exists():
    with open(out_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)
