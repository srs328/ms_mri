import pytest

from mri_data import file_manager as dfm


@pytest.fixture
def dataroot():
    return "/mnt/h/3Tpioneer_bids"


def test_filter_first_ses(dataroot):
    dataset = dfm.scan_3Tpioneer_bids(dataroot)
    dataset = dfm.filter_first_ses(dataset)

    subjects = set()
    for scan in dataset:
        subjects.add(scan.subid)

    for sub in subjects:
        scans = dataset.retrieve(subid=sub)
        assert len(scans) == 1
