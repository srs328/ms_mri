import pytest

from mri_data import file_manager
from mri_data.file_manager import DataSet, Scan, scan_3Tpioneer_bids


@pytest.fixture
def dataroot():
    return "/mnt/h/3Tpioneer_bids"


@pytest.fixture
def scanid_list():
    return [
        (1010, 20180208),
        (1011, 20180911),
        (1019, 20190608),
        (1033, 20171117),
        (1065, 20170127),
        (1080, 20180416),
        (1109, 20180303),
        (1119, 20161010),
        (1152, 20170529),
        (1163, 20180907),
        (1188, 20200720),
        (1191, 20190124),
        (1234, 20180214),
        (1259, 20200803),
        (1265, 20180127),
        (1272, 20211105),
        (1280, 20220317),
        (1293, 20161129),
        (1321, 20201020),
        (1355, 20210104),
        (1437, 20210503),
        (1486, 20210224),
        (1498, 20210602),
        (1518, 20220216),
        (1540, 20201222),
        (1547, 20220321),
        (1548, 20210628),
        (2081, 20170204),
        (2083, 20170502),
        (2097, 20171223),
        (2126, 20181224),
        (2132, 20190825),
        (2144, 20190422),
        (2146, 20191017),
        (2164, 20200113),
        (2187, 20200731)
    ]


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


def test_find_label_handles_suffix_list(scanid):
    label_prefix = "choroid_t1_flair"
    suffix_list = ["CH", "ED", "DT"]
    
    "choroid_t1_flair-CH.nii"