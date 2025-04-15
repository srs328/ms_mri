from loguru import logger
from pathlib import Path
import json
import os

from monai_training import preprocess
from mri_data.file_manager import DataSet, scan_3Tpioneer_bids, filter_first_ses

from monai.apps.auto3dseg import (
    AlgoEnsembleBestN,
    AlgoEnsembleBuilder,
    import_bundle_algo_history,
)


def get_inference_scans(
    dataset_train: DataSet, inference_root: Path, inference_name: str
) -> DataSet:
    dataroot = dataset_train.dataroot

    def inference_exists(dataset: DataSet) -> DataSet:
        count = 0
        dataset_new = DataSet(dataset.dataroot)
        for scan in dataset:
            if not (inference_root / scan.relative_path / inference_name).is_file():
                dataset_new.append(scan)
            else:
                count += 1
        logger.info(f"{count} scans already have inference")
        return dataset_new

    # dataset_train2 has the same subject/sessions that are in dataset_train but with a subset of the keys
    #   so that they can be compared to scans in the full data set when getting the set difference
    dataset_proc = preprocess.DataSetProcesser.new_dataset(
        dataroot, scan_3Tpioneer_bids, filters=[filter_first_ses, inference_exists]
    )
    dataset_full = dataset_proc.dataset
    dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])
    dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))

    return dataset_inference


def infer(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    save_dir = config['save_dir']
    dataroot = config['dataroot']

    if save_dir == "pwd":
        save_dir = os.getcwd()
    if dataroot == "pwd":
        dataroot = os.getcwd()

    network_bundle_path = config['network_bundle_path']
    task_name = config['task_name']

    save_params = {
        "_target_": "SaveImage",
        "output_dir": save_dir,
        "data_root_dir": dataroot,
    }
    save_params.update(config['save_params'])

    # change this so there's an option for relative paths where whatever is in the 
    # filelist is just appended to dataroot
    files = config['files']
    if isinstance(files, list):
        image_files = files
    elif files == "scan":
        image_files = get_files_from_dataroot(dataroot)
    elif files.split(".")[-1] == "txt":
        image_files = read_filelist(files)
    else:
        raise ValueError("files attribute should be a list of filepaths, 'scan', or path to txt file")
    
    images = image_list(image_files, dataroot)

    print(images[0]['image'])

    print(f"Will run inference on {len(images)} scans")

    datalist = {"testing": images}

    datalist_file = os.path.join(save_dir, "datalist.json")
    with open(datalist_file, "w") as f:
        json.dump(datalist, f, indent=4)

    task = {
        "name": task_name,
        "task": "segmentation",
        "modality": "MRI",
        "datalist": datalist_file,
        "dataroot": dataroot,
    }

    task_file = os.path.join(save_dir, "inference-task.json")
    with open(task_file, "w") as f:
        json.dump(task, f, indent=4)

    input_cfg = task_file  # path to the task input YAML file created by the users

    history = import_bundle_algo_history(network_bundle_path, only_trained=True)

    ## model ensemble
    n_best = 5
    builder = AlgoEnsembleBuilder(history, input_cfg)
    builder.set_ensemble_method(AlgoEnsembleBestN(n_best=n_best))
    ensemble = builder.get_ensemble()
    ensemble(pred_param={"image_save_func": save_params})
    

def image_list(image_files: list, dataroot: str) -> list[dict]:
    images = []
    for im in image_files:
        images.append({"image": os.path.join(dataroot, im)})
    return images


def get_files_from_dataroot(dataroot) -> list[str]:
    image_files = [file.name for file in os.scandir(dataroot) if file.is_file()]
    return image_files
    

def read_filelist(filelist) -> list[str]:
    with open(filelist, 'r') as f:
        image_files = [line.rstrip() for line in f.readlines()]
    return image_files