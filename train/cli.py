from collections.abc import Sequence
import copy
import json
from loguru import logger
import os
from pathlib import Path
from subprocess import CalledProcessError
import sys
import time

from train import data_file_manager as dfm
from train import preprocess
from train import training

logger.remove(0)
logger.add(sys.stderr, level="INFO", format="{level} | {message}")


# later make the label use a glob in case there are initials after label name
def prepare_dataset(dataroot, modality, label):
    if isinstance(modality, str):
        modality = [modality]
    if len(modality) > 1:
        modality = list(modality)
        modality.sort()
        image_name = "_".join(modality) + ".nii.gz"
        image_ids = [(i, mod) for i, mod in enumerate(modality)]
    else:
        image_name = f"{modality[0]}.nii.gz"
        image_ids = [(0, modality[0])]

    if isinstance(label, str):
        label = [label]
    if len(label) > 1:
        label = list(label)
        label.sort()
        label_name = "_".join(label) + ".nii.gz"
        # ? combine_labels() returns label_ids, idk if I should set that here or then
        label_ids = [(2**i, lab) for i, lab in enumerate(label)]
    else:
        label_name = f"{label[0]}.nii.gz"
        label_ids = [(1, label[0])]  #! this might not be true, revisit

    dataset = dfm.scan_3Tpioneer_bids(dataroot, modality, label)
    dataset_copy = dfm.DataSet("DataSet", dfm.Scan)
    for scan in dataset:
        if scan.label is None and len(label) > 1:
            try:
                preprocess.combine_labels(scan, label, label_name)
            except FileNotFoundError as e:
                continue
            except CalledProcessError as e:
                logger.error("Something went wrong merging labels")
                raise
            else:
                scan.label = scan.root / label_name
                logger.info(f"Saved {scan.label}")

        if scan.image is None and len(modality) > 1:
            base_images = [scan.root / f"{mod}.nii.gz" for mod in modality]
            merged_image = scan.root / image_name
            try:
                preprocess.merge_images(base_images, merged_image)
            except FileNotFoundError as e:
                continue
            except CalledProcessError as e:
                logger.error("Something went wrong merging images")
                raise
            else:
                scan.image = scan.root / merged_image
                logger.info(f"Saved {scan.image}")

        dataset_copy.append(scan)

    dataset_info = {"image_info": image_ids, "label_info": label_ids}

    return dataset_copy, dataset_info


def save_dataset(dataset, save_path, dataset_info=None):
    if dataset_info is not None:
        struct = dataset_info
    else:
        struct = {}
    struct.update({"data": dataset.serialize()})

    with open(save_path, "w") as f:
        json.dump(struct, f, indent=4)
