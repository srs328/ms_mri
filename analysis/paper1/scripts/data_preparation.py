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

mod = sys.argv[1]

config = {
    "t1": "t1_choroid_pineal_pituitary_T1-1_pred",
    "flair": "flair_choroid_pineal_pituitary_FLAIR-1_pred",
    "t1_2": "t1_choroid_pineal2_pituitary_T1-1_pred"
}


drive_root = fm.get_drive_root()
msmri_home = Path("/home/srs-9/Projects/ms_mri")
inference_root = drive_root / "srs-9" / "3Tpioneer_bids_predictions"
dataroot = drive_root / "3Tpioneer_bids"
clinical_data_root = drive_root / "Secure_Data" / "Large"
data_file_folder = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/data0")
inf_label = config[mod]


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


dataset_proc = DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)
full_dataset = dataset_proc.dataset
dataset_proc.prepare_labels(
    ["choroid_t1_flair", "pineal", "pituitary"], ["CH", "SRS", "ED", "DT"]
)
dataset = dataset_proc.dataset

inference_dataset_proc = DataSetProcesser.new_dataset(
    inference_root, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)
inference_dataset_proc.prepare_labels(inf_label)
inference_dataset = inference_dataset_proc.dataset


segs = {}
for scan in dataset:
    segs[scan.subid] = scan.label_path
    df.loc[int(scan.subid), ("sub-ses",)] = scan.relative_path
    df.loc[int(scan.subid), ("label_folder",)] = scan.label_path.relative_to(drive_root)
    df.loc[int(scan.subid), ("label",)] = scan.label

for scan in inference_dataset:
    segs[scan.subid] = scan.label_path
    df.loc[int(scan.subid), ("sub-ses",)] = scan.relative_path
    df.loc[int(scan.subid), ("label_folder",)] = scan.label_path.relative_to(drive_root)
    df.loc[int(scan.subid), ("label",)] = scan.label


try:
    df.insert(7, "tiv", None)
except ValueError:
    pass
try:
    df.insert(7, "pituitary_volume", None)
except ValueError:
    pass
try:
    df.insert(7, "pineal_volume", None)
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
volumes = dict(pituitary=[], pineal=[], choroid=[], tiv=[], subid=[])
subids = [subid for subid, _ in df.iterrows()]
for subid, _ in tqdm(df.iterrows(), total=len(df)):
    scan = dataset.find_scan(subid=str(subid))
    if len(scan) == 0:
        scan = inference_dataset.find_scan(subid=str(subid))
    if len(scan) == 0:
        continue
    scan = scan[0]

    try:
        vol_stats = utils.compute_volume(
            scan.label_path, index_mask_file=scan.label_path
        )
    except Exception:
        continue
    try:
        roi_vols = [stat[1] for stat in vol_stats]
    except Exception:
        roi_vols = [None, None, None]

    if len(roi_vols) < 3:
        continue

    scan = full_dataset.find_scan(subid=str(subid))[0]
    try:
        tiv = utils.compute_volume(scan.root / "t1.mask.nii.gz")[1]
    except Exception:
        continue

    df.loc[subid, "choroid_volume"] = roi_vols[0]
    df.loc[subid, "pineal_volume"] = roi_vols[1]
    df.loc[subid, "pituitary_volume"] = roi_vols[2]
    df.loc[subid, "tiv"] = tiv

    volumes["choroid"].append(roi_vols[0])
    volumes["pineal"].append(roi_vols[1])
    volumes["pituitary"].append(roi_vols[2])
    volumes["tiv"].append(tiv)
    volumes["subid"].append(subid)

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

df.to_csv(f"{mod}_data_full.csv")
