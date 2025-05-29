import compute_jacobians
import create_hipsthomas_jacobians
import get_hipsthomas_volumes
from mri_data import file_manager as fm
import json
import re

drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
work_home = drive_root / "srs-9/longitudinal"

subids = []
for folder in work_home.glob("sub*"):
    subids.append(re.match(r"sub(\d{4})", folder.name)[1])

# print(subjects)

# # subids = ['2075', '1023', '1038', '1098']
# subids = ['1326']
# subjects = [2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301]
# subids = [str(subid) for subid in subjects]
subids = ['1042']
for subid in subids:
    if subid in ['1196', '1182', '2119', '2152', '1341', '1441', '1546', '2039']:
        continue
    compute_jacobians.main(subid, dataroot, work_home)
    create_hipsthomas_jacobians.main(subid, dataroot, work_home)
    try:
        get_hipsthomas_volumes.main(subid, dataroot, work_home)
    except Exception:
        continue