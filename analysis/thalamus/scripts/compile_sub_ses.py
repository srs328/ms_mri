import csv
import os
from mri_data.file_manager import scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

save_dir = "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0"

drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
dataset_proc = DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
)

dataset = dataset_proc.dataset
dataset.sort()

save_file = os.path.join(save_dir, "subject-sessions.csv")
with open(save_file, 'w') as f:
    writer = csv.writer(f)
    for scan in dataset:
        writer.writerow([scan.subid, scan.sesid])
