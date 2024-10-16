import os
from pathlib import Path
import numpy as np
import json

import mri_data
import monai_training

from monai.apps.auto3dseg import (
    AlgoEnsembleBestN,
    AlgoEnsembleBuilder,
    import_bundle_algo_history,
)
from monai.utils.enums import AlgoKeys

from mri_data import utils
from mri_data.file_manager import scan_3Tpioneer_bids, Scan, DataSet
from monai_training import preprocess

msmri_home = Path("/home/srs-9/Projects/ms_mri")
training_work_dirs = Path("/mnt/h/training_work_dirs")

dataroot = "/mnt/h/3Tpioneer_bids"
work_dir = msmri_home / "training_work_dirs" / "pineal1"
train_dataset_file = work_dir / "training-dataset.json"


# get all but the train subjects for inference
dataset_train, _ = preprocess.load_dataset(train_dataset_file)

dataset_proc = preprocess.DataSetProcesser.new_dataset(
    dataroot, scan_3Tpioneer_bids, filters=["first_ses"]
)
dataset_full = dataset_proc.dataset
dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])
dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))


# prepare the inference scans
dataset_proc = preprocess.DataSetProcesser(dataset_inference)
dataset_proc.prepare_images(["flair", "t1"])

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

save_dir = Path("/mnt/h/3Tpioneer_bids_predictions")

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
