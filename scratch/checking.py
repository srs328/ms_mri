from pathlib import Path
import json
from mri_data import file_manager as fm
from monai_training.preprocess import load_dataset

dataroot = "/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids"


def initialize_dataset():
    return fm.scan_3Tpioneer_bids(dataroot)


def get_scan(image=None, label=None):
    subid = 1010
    sesid = 20180208
    scan = fm.Scan.new_scan(dataroot, subid, sesid)
    if image is not None:
        scan.set_image(image)
    if label is not None:
        scan.set_label(label)
    return scan


dataroot = Path("/mnt/h/3Tpioneer_bids")
dataset_file = "/mnt/h/training_work_dirs/choroid_pineal_pituitary2/dataset.json"

with open(dataset_file, "r") as f:
    struct = json.load(f)

info = struct["info"]
dataset_list = struct["data"]

dataset = fm.scan_3Tpioneer_bids(
    dataroot, image="flair.nii.gz", label="pineal-SRS.nii.gz"
)

dataset = fm.filter_has_image(dataset)
dataset = fm.filter_has_label(dataset)

# dataset = dfm.DataSet(records=dataset_list)
# scan = dataset[0]
thoo = 4


"""
import checking
scan = checking.get_scan()

from mri_data import data_file_manager as dfm
dataset = dfm.scan_3Tpioneer_bids("/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids", image="t1.nii.gz", label="choroid_t1_flair-CH.nii.gz")
scan = dataset[0]

/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids/sub-ms1019/ses-20190608

/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids/sub-ms1010/ses-20180208
/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids/sub-1010/ses-20180208
"""
