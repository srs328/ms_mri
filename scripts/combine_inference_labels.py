import contextlib
import io
import os
from pathlib import Path
import platform
import json
from loguru import logger
import sys
import tqdm

from mri_data.file_manager import DataSet, scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

logger.remove()
logger.add(sys.stderr, level="INFO")


def main():
    drive_root = fm.get_drive_root()
    projects_root = Path("/home/srs-9/Projects")
    inference_root = drive_root / "3Tpioneer_bids_predictions"

    inferred_label_names = [
        "flair.t1_choroid_resegment_pred",
        "flair.t1_pineal_pred",
        "t1_pituitary_pred",
    ]

    dataset_proc = DataSetProcesser.new_dataset(
        inference_root, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
    )
    dataset = dataset_proc.dataset
    dataset.sort()

    for i, scan in tqdm(enumerate(dataset), total=len(dataset)):
        try:
            label_name, label_values = utils.combine_labels(
                scan, inferred_label_names, utils.power_of_two
            )
        except FileNotFoundError as e:
            logger.error(e)
            continue


if __name__ == "__main__":
    main()
