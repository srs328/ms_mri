import json
from loguru import logger
import os
from pathlib import Path
import pytest
import re
import shutil
import sys

from monai_training.preprocess import DataSetProcesser
from mri_data import file_manager as fm
from mri_data.loggers import Formatter

current_dir = Path(__file__).absolute().parent
logger.remove()
formater = Formatter()
logger.add(sys.stderr, level="DEBUG", format=formater.format)
logger.add(current_dir / "new_files.log", serialize=True, level="DEBUG")

#! why aren't all the logs from preprocess showing up in the tests? (e.g. logger.info on line 149)


@pytest.fixture
def dataroot():
    # return "/home/srs-9/Projects/ms_mri/tests/data"
    return "/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids"


@pytest.fixture
def log_file():
    yield current_dir / "new_files.log"

    # teardown
    delete_new_files(current_dir / "new_files.log")


@pytest.fixture
def label_onesubj_only(dataroot):
    root = Path(dataroot) / "sub-ms1010" / "ses-20180208"
    label_name = "thoo"
    dst_path = root / f"{label_name}.nii.gz"
    shutil.copy(root / "lesion_index.t3m20.nii.gz", dst_path)
    yield label_name
    os.remove(dst_path)


@pytest.fixture
def multilabel_onesubj_only(dataroot):
    root = Path(dataroot) / "sub-ms1010" / "ses-20180208"
    label_names = ["foo", "bar", "baz"]
    for lab in label_names:
        dst_path = root / f"{lab}.nii.gz"
        shutil.copy(root / "lesion_index.t3m20.nii.gz", dst_path)
    yield label_names

    for lab in label_names:
        dst_path = root / f"{lab}.nii.gz"
        os.remove(dst_path)

    os.remove(root / "bar.baz.foo.nii.gz")


def test_prepare_dataset_badlabel(dataroot):
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels("foo")
    dataset_proc.prepare_images("flair")
    assert len(dataset_proc.dataset) == 0


def test_prepare_dataset_onelabel(dataroot, label_onesubj_only):
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels(label_onesubj_only)
    dataset_proc.prepare_images("flair")
    assert len(dataset_proc.dataset) == 1
    assert dataset_proc.dataset[0].label is not None
    assert dataset_proc.dataset[0].subid == "1010"


def test_prepare_dataset_onemultilabel(dataroot, multilabel_onesubj_only):
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels(multilabel_onesubj_only)
    dataset_proc.prepare_images("flair")
    assert len(dataset_proc.dataset) == 1
    assert (
        dataset_proc.dataset[0].label_path
        == dataset_proc.dataset[0].root / "bar.baz.foo.nii.gz"
    )
    assert dataset_proc.dataset[0].subid == "1010"
    assert os.path.exists(dataset_proc.dataset[0].root / "bar.baz.foo.nii.gz")


def test_prepare_dataset_multilabel(dataroot, log_file):
    with open(log_file, "w"):
        pass
    label = ["pineal", "choroid_t1_flair", "pituitary"]
    suffix_list = ["CH", "SRS", ""]
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels(label, suffix_list)
    assert len(dataset_proc.dataset) > 0
    assert (
        "label_info" in dataset_proc.info
        and dataset_proc.info["label_info"] is not None
    )

    assert re.match("choroid_t1_flair.pineal.pituitary", dataset_proc.label_name)

    re_label = re.compile(
        r"choroid_t1_flair(-[A-Z]+)?\.pineal(-[A-Z]+)?\.pituitary(-[A-Z]+)?\.nii\.gz"
    )
    for scan in dataset_proc.dataset:
        print(scan.label)
        assert re_label.match(scan.label)
        assert scan.label_path.is_file()


def test_prepare_dataset_multiimage(dataroot, log_file):
    with open(log_file, "w"):
        pass
    modality = ["t1", "flair"]
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_images(modality)
    assert len(dataset_proc.dataset) > 0
    assert (
        "image_info" in dataset_proc.info
        and dataset_proc.info["image_info"] is not None
    )

    assert re.match("flair.t1", dataset_proc.image_name)

    re_image = re.compile(r"flair.t1")
    for scan in dataset_proc.dataset:
        print(scan.image)
        assert re_image.match(scan.image)
        assert scan.image_path.is_file()


def delete_new_files(file):
    with open(file, "r") as f:
        for line in f.readlines():
            try:
                json_struct = json.loads(line.strip())
            except json.decoder.JSONDecodeError:
                continue
            try:
                if "new_file" in json_struct["record"]["extra"]:
                    os.remove(json_struct["record"]["extra"]["new_file"])
            except KeyError:
                continue
