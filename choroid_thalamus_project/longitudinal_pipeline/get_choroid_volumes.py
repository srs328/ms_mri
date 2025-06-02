# %%
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess
from mri_data import file_manager as fm
import re
from tqdm import tqdm
from datetime import datetime


#! Update this to use the individual files hips thomas creates instead of how it is now 


def analyze_single_mask(index_mask, jacobian):
    cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
    m_result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        m_val = float(m_result.stdout)
    except (TypeError, ValueError):
        m_val = None

    cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
    v_result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        v_val = float(v_result.stdout.split(" ")[1])
    except (AttributeError, TypeError, IndexError, ValueError):
        v_val = None

    return m_val, v_val

def do_fslstats(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", "r") as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    index_mask = work_dir / "segmentations" / "choroid_aschoplex.nii.gz"
    cmd = ["fslstats", index_mask, "-V"]
    v_result = subprocess.run(cmd, capture_output=True, text=True)
    v_val = float(v_result.stdout.split(" ")[1])

    m_vals = []
    for sesid in sessions:
        jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
        cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
        m_result = subprocess.run(cmd, capture_output=True, text=True)
        m_vals.append(float(m_result.stdout))
        
    return v_val, m_vals, sessions


drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
work_home = drive_root / "srs-9/longitudinal"
data_dir = Path("/home/srs-9/Projects/ms_mri/data")
date_format = "%Y%m%d"

subids = []
for folder in work_home.glob("sub*"):
    subids.append(int(re.match(r"sub(\d{4})", folder.name)[1]))

subids.sort()
subids = [str(subid) for subid in subids]
subids.remove('1225')

data = []
for subid in tqdm(subids):
    print(subid)
    v_val, m_vals, sessions = do_fslstats(subid, dataroot, work_home)

    delta = datetime.strptime(str(sessions[1]), date_format) - datetime.strptime(str(sessions[0]), date_format)
    t_delta = delta.days / 365
    v1 = v_val / m_vals[0]
    v2 = v_val / m_vals[1]

    data.append({
        'template_volume': v_val,
        'volume1': v1,
        'volume2': v2,
        'm1': m_vals[0],
        'm2': m_vals[1],
        't1': sessions[0],
        't2': sessions[1],
        't_delta': t_delta
    })

    # data['volume'].append(v_val)
    # data['m1'].append(m_vals[0])
    # data['m2'].append(m_vals[1])
    # data['t1'].append(sessions[0])
    # data['t2'].append(sessions[1])

index = [int(subid) for subid in subids]
df = pd.DataFrame(data, index=index)
df.to_csv(data_dir / "choroid_longitudinal_changes.csv")