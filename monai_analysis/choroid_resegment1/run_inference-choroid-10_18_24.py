import contextlib
import io
import os
from pathlib import Path
import platform
import json
from loguru import logger

from monai.apps.auto3dseg import (
    AlgoEnsembleBestN,
    AlgoEnsembleBuilder,
    import_bundle_algo_history,
)
from monai.utils.enums import AlgoKeys

from mri_data import file_manager as fm
from mri_data.file_manager import scan_3Tpioneer_bids, DataSet, filter_first_ses
from monai_training import preprocess


do_preparation = False
do_inference = True


log_dir = ".logs"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logger.add(
    os.path.join(log_dir, "file_{time:%Y_%m_%d}.log"), rotation="6h", level="DEBUG"
)

#! Set these variables
work_dir_name = "choroid_resegment1"
# train_dataset_file_name = "training-dataset-desktop1.json"
train_dataset_file_name = "training-dataset.json"

prediction_postfix = "choroid_resegment_pred"
task_name = "infer_choroid"
modalities = ["flair", "t1"]
save_folder = "3Tpioneer_bids_predictions"

# -----------------

drive_root = fm.get_drive_root()
projects_root = Path("/home/srs-9/Projects")

msmri_home = projects_root / "ms_mri"
# training_work_dirs = drive_root / "training_work_dirs" #? don't know why I did this
training_work_dirs = msmri_home / "training_work_dirs"

# dataroot = "/media/hemondlab/Data/3Tpioneer_bids"
dataroot = drive_root / "3Tpioneer_bids"
work_dir = training_work_dirs / work_dir_name
train_dataset_file = work_dir / train_dataset_file_name

prediction_filename = (
    ".".join(sorted(modalities)) + "_" + prediction_postfix + ".nii.gz"
)
logger.info(prediction_filename)

taskfile_name = "inference-task.json"
task_file = os.path.join(work_dir, taskfile_name)
save_dir = drive_root / save_folder

# -----------------


def inference_exists(dataset: DataSet) -> DataSet:
    count = 0
    dataset_new = DataSet(dataset.dataroot)
    for scan in dataset:
        if not (save_dir / scan.relative_path / prediction_filename).is_file():
            dataset_new.append(scan)
        else:
            count += 1
    logger.info(f"{count} scans already have inference")
    return dataset_new

# -----------------


if do_preparation:
    # scan the dataroot to get all the scans
    dataset_proc = preprocess.DataSetProcesser.new_dataset(
        dataroot, scan_3Tpioneer_bids, filters=[filter_first_ses, inference_exists],
        suppress_exceptions=True
    )
    dataset_full = dataset_proc.dataset

    # load the scans that were used in the training
    dataset_train, _ = preprocess.load_dataset(train_dataset_file)
    # correct the dataroot in case using a different system
    dataset_train.dataroot = dataroot

    # copy the training dataset but with only the bare attributes
    dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])
    dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))

    # prepare the inference scans
    dataset_proc = preprocess.DataSetProcesser(dataset_inference)
    dataset_proc.prepare_images(["flair", "t1"])
    dataset_proc.dataset.sort(key=lambda s: s.subid)

    # save the config files
    images = []
    for scan in dataset_proc.dataset:
        infile: Path = scan.image_path
        images.append({"image": str(infile.relative_to(dataset_proc.dataset.dataroot))})

    logger.info(f"Will run inference on {len(images)} scans")

    datalist = {"testing": images}

    datalist_file = work_dir / "datalist.json"
    with open(datalist_file, "w") as f:
        json.dump(datalist, f)

    task = {
        "name": task_name,
        "task": "segmentation",
        "modality": "MRI",
        "datalist": str(work_dir / "datalist.json"),
        "dataroot": str(dataroot),
    }

    with open(task_file, "w") as f:
        json.dump(task, f)

# -----------------


if do_inference:
    output = io.StringIO

    # init inference model
    # path to the task input YAML file created by the users
    input_cfg = task_file  # path to the task input YAML file created by the users
    history = import_bundle_algo_history(work_dir, only_trained=True)

    ## model ensemble
    n_best = 5
    builder = AlgoEnsembleBuilder(history, input_cfg)
    builder.set_ensemble_method(AlgoEnsembleBestN(n_best=n_best))
    ensemble = builder.get_ensemble()
    save_params = {
        "_target_": "SaveImage",
        "output_dir": save_dir,
        "data_root_dir": dataroot,
        "output_postfix": prediction_postfix,
        "separate_folder": False,
    }

    pred = ensemble(pred_param={"image_save_func": save_params})
