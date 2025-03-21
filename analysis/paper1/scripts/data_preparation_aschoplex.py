import pandas as pd
from loguru import logger
from pathlib import Path
from tqdm import tqdm
import os
import re
import sys

from mri_data.file_manager import scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

#! don't run yet, haven't checked if it worked. just copied the previously created data files

logger.remove()


drive_root = fm.get_drive_root()
msmri_home = Path("/home/srs-9/Projects/ms_mri")
inference_root = drive_root / "srs-9" / "3Tpioneer_bids_predictions"
dataroot = drive_root / "3Tpioneer_bids"
clinical_data_root = drive_root / "Secure_Data" / "Large"
data_file_folder = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/data0")
ascho_labelroot = drive_root / "srs-9/aschoplex/test1_inference"

save_prefix = "t1_aschoplex"

def subject_to_subid(subject):
    if not isinstance(subject, str):
        return None
    re_match = re.match(r"ms(\d{4})", subject)
    if re_match:
        return_val = int(re_match[1])
        return return_val
    else:
        return None


df = pd.read_csv(clinical_data_root / "Clinical_Data_All_updated.csv")
df = df.convert_dtypes()


new_columns = {
    "ID": "subject",
    "age_at_obs_start": "age",
}
df.rename(columns=new_columns, inplace=True)
df["subid"] = df["subject"].apply(subject_to_subid)
df.drop(df[df["subid"].isna()].index, inplace=True)
df["subid"] = df["subid"].astype(int)
df = df.set_index("subid")

new_columns = {}
for col in df.columns:
    new_columns[col] = col.replace(" ", "_")
df.rename(columns=new_columns, inplace=True)


ascho_labelfiles = [Path(item.path) for item in os.scandir(ascho_labelroot) if item.is_file()]
ascho_labels = {}
for file in ascho_labelfiles:
    sub = re.match(r"MRI_(\d{4}).+", file.name)[1]
    ascho_labels[sub] = file


dataset_proc = DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)
full_dataset = dataset_proc.dataset
dataset_proc.prepare_labels(
    ["choroid_t1_flair"], ["CH", "SRS", "ED", "DT"]
)
dataset = dataset_proc.dataset

for scan in dataset:
    df.loc[int(scan.subid), ("sub-ses",)] = str(scan.relative_path)
    # df.loc[int(scan.subid), ("label_folder",)] = str(scan.label_path.relative_to(drive_root))
    df.loc[int(scan.subid), ("label_folder",)] = str(scan.label_path.parent)
    df.loc[int(scan.subid), ("label",)] = scan.label

for sub in ascho_labels:
    scan = full_dataset.find_scan(subid=sub)[0]
    df.loc[int(sub), ("sub-ses",)] = str(scan.relative_path)
    df.loc[int(sub), ("label_folder",)] = str(ascho_labelroot)
    df.loc[int(sub), ("label",)] = ascho_labels[sub].name


try:
    df.insert(7, "tiv", None)
except ValueError:
    pass
try:
    df.insert(7, "choroid_volume", None)
except ValueError:
    pass
try:
    df.insert(3, "flair_contrast", None)
except ValueError:
    pass


print("Computing Volumes")
subids = [subid for subid, _ in df.iterrows()]
for subid, row in tqdm(df.iterrows(), total=len(df)):
    if not isinstance(row['label_folder'], str):
        continue

    label_path = Path(row['label_folder']) / row['label']
    try:
        vol_stats = utils.compute_volume(
            str(label_path), index_mask_file=str(label_path)
        )
    except Exception:
        continue
    try:
        roi_vol = vol_stats[1]
    except Exception:
        roi_vol = None

    scan = full_dataset.find_scan(subid=str(subid))[0]
    try:
        tiv = utils.compute_volume(scan.root / "t1.mask.nii.gz")[1]
    except Exception:
        tiv = None

    df.loc[subid, "choroid_volume"] = roi_vol
    df.loc[subid, "tiv"] = tiv

    files = [
        item.name
        for item in os.scandir(scan.root)
        if item.is_file() and re.match("flair=", item.name)
    ]
    if len(files) == 0:
        is_contrast = None
    else:
        is_contrast_file = files[0]
        match = re.match(r"flair=(\w+)con", is_contrast_file)
        is_contrast = match[1]

    df.loc[subid, "flair_contrast"] = is_contrast

df.to_csv(f"{save_prefix}_data_full.csv")
