import os
from pathlib import Path
import json
from loguru import logger

# add logic that discludes a scan from list if the inference already exists for it

from monai.apps.auto3dseg import (
    AlgoEnsembleBestN,
    AlgoEnsembleBuilder,
    import_bundle_algo_history,
)
from monai.utils.enums import AlgoKeys

from mri_data import utils
from mri_data.file_manager import scan_3Tpioneer_bids, Scan, DataSet, filter_first_ses
from monai_training import preprocess


log_dir = ".logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logger.add(os.path.join(log_dir, "file_{time:%Y_%m_%d}.log"), rotation="6h", level='DEBUG')


projects_root = Path("/home/hemondlab/Dev")
drive_root = Path("/media/smbshare")

msmri_home = projects_root / "ms_mri"
training_work_dirs = drive_root / "training_work_dirs"

# dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataroot = drive_root / "3Tpioneer_bids"
work_dir = msmri_home / "training_work_dirs" / "pineal1"
train_dataset_file = work_dir / "training-dataset-desktop1.json"

def inference_exists(dataset: DataSet) -> DataSet:
    dataset_new = DataSet()
    for scan in dataset:
        if not (scan.root / "flair.t1_pineal_pred.nii.gz").is_file():
            dataset_new.append(scan)
    return dataset_new


# get all but the train subjects for inference
dataset_train, _ = preprocess.load_dataset(train_dataset_file)

dataset_proc = preprocess.DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=[filter_first_ses, inference_exists]
)
dataset_full = dataset_proc.dataset
dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])
dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))


# prepare the inference scans
dataset_proc = preprocess.DataSetProcesser(dataset_inference)
dataset_proc.prepare_images(["flair", "t1"])

dataset_proc.dataset.sort()

# save the config files
images = []
for scan in dataset_proc.dataset:
    infile: Path = scan.image_path
    images.append({"image": str(infile.relative_to(dataset_proc.dataset.dataroot))})

datalist = {"testing": images}

datalist_file = work_dir / "datalist.json"
with open(datalist_file, "w") as f:
    json.dump(datalist, f)

task = {
    "name": "infer_pineal",
    "task": "segmentation",
    "modality": "MRI",
    "datalist": str(work_dir / "datalist.json"),
    "dataroot": str(dataroot),
}

task_file = os.path.join(work_dir, "inference-task.json")
with open(task_file, "w") as f:
    json.dump(task, f)


# init inference model
input_cfg = (
    work_dir / "inference-task.json"
)  # path to the task input YAML file created by the users
history = import_bundle_algo_history(work_dir, only_trained=True)

save_dir = Path("/media/smbshare/3Tpioneer_bids_predictions")

## model ensemble
n_best = 5
builder = AlgoEnsembleBuilder(history, input_cfg)
builder.set_ensemble_method(AlgoEnsembleBestN(n_best=n_best))
ensemble = builder.get_ensemble()
save_params = {
    "_target_": "SaveImage",
    "output_dir": save_dir,
    "data_root_dir": dataroot,
    "output_postfix": "pineal_pred",
    "separate_folder": False,
}

pred = ensemble(pred_param={"image_save_func": save_params})
