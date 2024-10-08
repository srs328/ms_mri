import os
from pathlib import Path
import pytest
import shutil

from monai_training import preprocess


@pytest.fixture
def dataroot():
    # return "/home/srs-9/Projects/ms_mri/tests/data"
    return "/home/hemondlab/Dev/ms_mri/Data/3Tpioneer_bids"


@pytest.fixture
def label_onesubj_only():
    root = Path("/home/srs-9/Projects/ms_mri/tests/data/sub-ms1002/ses-20200521")
    label_name = "thoo"
    dst_path = root / f"{label_name}.nii.gz"
    shutil.copy(root / "lesion_index.t3m20.nii.gz", dst_path)
    yield label_name
    os.remove(dst_path)


@pytest.fixture
def multilabel_onesubj_only():
    root = Path("/home/srs-9/Projects/ms_mri/tests/data/sub-ms1001/ses-20170215")
    label_names = ["foo", "bar", "baz"]
    for lab in label_names:
        dst_path = root / f"{lab}.nii.gz"
        shutil.copy(root / "lesion_index.t3m20.nii.gz", dst_path)
    yield label_names

    for lab in label_names:
        dst_path = root / f"{lab}.nii.gz"
        os.remove(dst_path)

    os.remove(root / "bar_baz_foo.nii.gz")


def test_prepare_dataset_badlabel(dataroot):
    dataset = preprocess.prepare_dataset(dataroot, "flair", "foo")
    assert len(dataset) == 0


def test_prepare_dataset_onelabel(dataroot, label_onesubj_only):
    dataset = preprocess.prepare_dataset(dataroot, "flair", label_onesubj_only)
    assert len(dataset) == 1
    assert dataset[0].label is not None
    assert dataset[0].subid == "1002"


def test_prepare_dataset_onemultilabel(dataroot, multilabel_onesubj_only):
    dataset = preprocess.prepare_dataset(dataroot, "flair", multilabel_onesubj_only)
    assert len(dataset) == 1
    assert dataset[0].label == dataset[0].root / "bar_baz_foo.nii.gz"
    assert dataset[0].subid == "1001"
    assert os.path.exists(dataset[0].root / "bar_baz_foo.nii.gz")


# test_prepare_dataset_badlabel(dataroot)
