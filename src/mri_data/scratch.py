# import preprocess
# import train
# import data_file_manager as dfm
# from train import cli
import json

from mri_data import utils
from mri_data.file_manager import scan_3Tpioneer_bids, Scan, DataSet
from monai_training import preprocess
from pathlib import Path

# data = "/home/srs-9/Projects/ms_mri/tests/data"

# dataset, info = cli.prepare_dataset(data, ("flair", "t1"), "pituitary")

# cli.save_dataset(dataset, "test.json", info)

# pituitary_file = "/home/srs-9/Projects/ms_mri/notes/tmp_pituitary.txt"
# choroid_file = "/home/srs-9/Projects/ms_mri/notes/tmp_choroid.txt"

# pituitary = set()
# choroid = set()
# with open(pituitary_file, "r") as f:
#     for line in f.readlines():
#         pituitary.add(line.strip())
# with open(choroid_file, "r") as f:
#     for line in f.readlines():
#         choroid.add(line.strip())

# diff = choroid - pituitary
# print(len(diff))
# print(diff)

msmri_home = Path("/home/srs-9/Projects/ms_mri")

dataroot = "/mnt/h/3Tpioneer_bids"
work_dir = msmri_home / "training_work_dirs" / "pineal1"
train_dataset_file = work_dir / "training-dataset.json"
dataset_train, _ = preprocess.load_dataset(train_dataset_file)

dataset_full = scan_3Tpioneer_bids(dataroot)
dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])

dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))
dataset_proc = preprocess.DataSetProcesser(dataset_inference)
dataset_proc.prepare_images(["flair", "t1"])
