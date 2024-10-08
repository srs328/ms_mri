from pathlib import Path
import pytest

from mri_data import utils
from mri_data.data_file_manager import Scan

@pytest.fixture
def dataroot():
    return "/mnt/h/3Tpioneer_bids"


@pytest.fixture
def scan():
    scan_root = Path("/mnt/h/3Tpioneer_bids/sub-ms1010/ses-20180208")
    return Scan(subid="1010", sesid="20180208", root=scan_root)


def test_find_label_returns_label(scan):
    prefix = "pineal"
    suffix_list = ["_SRS", "_ch"]
    label = utils.find_label(scan, prefix, suffix_list)
    assert label.name.lower() == (prefix + suffix_list[0] + ".nii.gz").lower()
    assert label.is_file()


def test_find_label_returns_exception(scan):
    prefix = "foo"
    suffix_list = ["_SRS", "_ch"]
    with pytest.raises(FileNotFoundError):
        utils.find_label(scan, prefix, suffix_list)
