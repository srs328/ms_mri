import pytest

from mri_data import file_manager
from mri_data.file_manager import DataSet, Scan, scan_3Tpioneer_bids


@pytest.fixture
def dataroot():
    return "/mnt/h/3Tpioneer_bids"


def test_empty_scan_3Tpioneer_bids(dataroot):
    dataset = scan_3Tpioneer_bids(dataroot)
    assert len(dataset) > 0
    assert isinstance(dataset, DataSet)
    for scan in dataset:
        assert isinstance(scan, Scan)
        assert scan.dataroot.is_dir()
        assert scan.root.is_dir()


def test_scan_3Tpioneer_bids(dataroot):
    dataset = scan_3Tpioneer_bids(
        dataroot, image="flair.nii.gz", label="pineal-SRS.nii.gz"
    )
    assert len(dataset) > 0
    assert isinstance(dataset, DataSet)

    dataset = file_manager.filter_has_image(dataset)
    dataset = file_manager.filter_has_label(dataset)

    for scan in dataset:
        assert isinstance(scan, Scan)
        assert scan.image_path.is_file()
        assert scan.label_path.is_file()
        assert scan.relative_path.parts[0] == f"sub-ms{scan.subid}"
        assert scan.relative_path.parts[1] == f"ses-{scan.sesid}"


def test_filter_first_ses(dataroot):
    dataset = scan_3Tpioneer_bids(dataroot)
    dataset = file_manager.filter_first_ses(dataset)

    subjects = set()
    for scan in dataset:
        subjects.add(scan.subid)

    for sub in subjects:
        scans = dataset.retrieve(subid=sub)
        assert len(scans) == 1
