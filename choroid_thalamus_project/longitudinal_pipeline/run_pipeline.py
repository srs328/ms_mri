import compute_jacobians
import create_hipsthomas_jacobians
import get_hipsthomas_volumes
from mri_data import file_manager as fm

drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
work_home = drive_root / "srs-9/longitudinal"
subids = ['1107', '1161', '1326', '1527']

for subid in subids:
    compute_jacobians.main(subid, dataroot, work_home)
    create_hipsthomas_jacobians.main(subid, dataroot, work_home)
    get_hipsthomas_volumes.main(subid, dataroot, work_home)