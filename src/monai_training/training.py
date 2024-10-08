from importlib.resources import files
import json
import os
from monai.apps.auto3dseg import AutoRunner
import nibabel as nibabel
import random
from dataclasses import dataclass

from mri_data.data_file_manager import DataSet


@dataclass
class DataList:
    work_dir: str
    training: list
    testing: list
    info: dict
    train_params: dict


def train(datalist_file):
    with open(datalist_file, "r") as f:
        struct = json.load(f)

    runner = AutoRunner(
        work_dir=struct.work_dir,
        algos=["swinunetr"],
        input={
            "modality": "MRI",
            "datalist": datalist_file,
            "dataroot": struct.dataroot,
        },
    )
    runner.set_training_params(struct.train_param)
    runner.run()


def setup_training(dataset, info, work_dir):
    train_params = load_train_params()

    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    dataset = assign_conditions(dataset, train_params.test_fract)
    train_data = []
    test_data = []
    for scan in dataset:
        if scan.cond == "tr" and scan.has_label():
            train_data.append({"image": str(scan.image), "label": str(scan.label)})
        elif scan.cond == "ts" and scan.has_label():
            test_data.append({"image": str(scan.image), "label": str(scan.label)})

    print(f"Train num total: {len(train_data)}")
    print(f"Test num: {len(test_data)}")

    datalist = {
        "work_dir": work_dir,
        "dataroot": dataset.dataroot,
        "info": info,
        "train_params": train_params,
        "testing": test_data,
        "training": [
            {"fold": i % train_params.n_folds, "image": c["image"], "label": c["label"]}
            for i, c in enumerate(train_data)
        ],
    }

    datalist_file = os.path.join(work_dir, "datalist.json")
    with open(datalist_file, "w") as f:
        json.dump(datalist, f)

    return datalist_file


def load_train_params():
    path = files("train") / "config" / "training_params.json"
    with open(path, "r") as f:
        train_params = json.load(f)
    return train_params


def assign_conditions(dataset: DataSet, fraction_ts) -> DataSet:
    scans_no_label = []
    for i, scan in enumerate(dataset):
        if not scan.has_label():
            scans_no_label.append(i)

    n_scans = len(dataset)
    n_ts = int(fraction_ts * n_scans)
    inds = [i for i in range(n_scans)]
    random.shuffle(inds)

    for i in scans_no_label:
        inds.remove(i)
        inds.insert(0, i)

    for i in inds[:n_ts]:
        dataset[i].cond = "ts"
    for i in inds[n_ts:]:
        dataset[i].cond = "tr"

    return dataset
