# %%
from pathlib import Path
import pandas as pd
import csv
import json
import re
import os
from datetime import datetime
from tqdm import tqdm
from loguru import logger

# %%
now = datetime.now()
log_filename = now.strftime(
    f"{os.path.basename(__file__).split('.')[0]}-%Y%m%d_T%H%M%S.log"
)
logger.remove()
logger.add(log_filename, mode="w")

# %%
dataroot     = Path("/home/shridhar.singh9-umw/data/longitudinal")
data_dir     = Path("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/data0")
sessions_file = Path("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/all_longitudinal_sessions.json")

with open(sessions_file) as f:
    subject_sessions = json.load(f)  # {subid_str: [sesid_int, ...]}

# %%
KEY_REF = [
    "1-THALAMUS", "2-AV", "4-VA", "5-VLa", "6-VLP", "7-VPL",
    "8-Pul", "9-LGN", "10-MGN", "11-CM", "12-MD-Pf", "13-Hb",
    "14-MTT", "26-Acc", "27-Cau", "28-Cla", "29-GPe", "30-GPi",
    "31-Put", "32-RN", "33-GP", "34-Amy",
]

def col_name(key):
    """Convert '8-Pul' -> 'Pul_8'"""
    return re.sub(r"(\d+)-([\w-]+)", r"\2_\1", key).replace("-", "_")

COL_NAMES = [col_name(k) for k in KEY_REF]


def parse_nuclei_vols(filepath):
    with open(filepath) as f:
        reader = csv.reader(f, delimiter=" ")
        return {row[0]: float(row[1]) for row in reader}


def load_session_vols(ses_root: Path):
    """
    Load left and right nucleiVols.txt for a session directory.
    Returns (left_vols, right_vols) dicts, or raises if files missing/malformed.
    """
    left_vols  = parse_nuclei_vols(ses_root / "left"  / "nucleiVols.txt")
    right_vols = parse_nuclei_vols(ses_root / "right" / "nucleiVols.txt")

    for side, vols in [("left", left_vols), ("right", right_vols)]:
        if list(vols.keys()) != KEY_REF:
            raise ValueError(f"Unexpected keys in {side} nucleiVols: {list(vols.keys())}")

    return left_vols, right_vols


# %%
rows_left  = []
rows_right = []
rows_full  = []

for subid, sessions in tqdm(subject_sessions.items(), total=len(subject_sessions)):
    subid = str(subid)
    subject_root = dataroot / f"sub{subid}"

    for sesid in sessions:
        sesid     = str(int(sesid))
        ses_root  = subject_root / sesid

        left_file  = ses_root / "left"  / "nucleiVols.txt"
        right_file = ses_root / "right" / "nucleiVols.txt"

        if not left_file.exists() or not right_file.exists():
            logger.info(f"Skipping sub{subid} ses{sesid} — nucleiVols.txt not found")
            continue

        try:
            left_vols, right_vols = load_session_vols(ses_root)
        except Exception as e:
            logger.warning(f"sub{subid} ses{sesid}: {e}")
            continue

        sessions_sorted = sorted([str(int(s)) for s in sessions])
        first_sesid = sessions_sorted[0]
        t_diff = (pd.to_datetime(sesid, format='%Y%m%d') - 
                pd.to_datetime(first_sesid, format='%Y%m%d')).days / 365.25

        base = {"subid": subid, "sesid": sesid, "t_diff": t_diff}

        left_row  = {**base, **{col_name(k): left_vols[k]  for k in KEY_REF}}
        right_row = {**base, **{col_name(k): right_vols[k] for k in KEY_REF}}
        full_row  = {**base, **{col_name(k): left_vols[k] + right_vols[k] for k in KEY_REF}}

        rows_left.append(left_row)
        rows_right.append(right_row)
        rows_full.append(full_row)

# %%
df_left  = pd.DataFrame(rows_left).set_index(["subid", "sesid"])
df_right = pd.DataFrame(rows_right).set_index(["subid", "sesid"])
df_full  = pd.DataFrame(rows_full).set_index(["subid", "sesid"])

# Sort by subject then session date (sesid is YYYYMMDD so lexicographic = chronological)
for df in [df_left, df_right, df_full]:
    df.sort_index(inplace=True)

print(f"Collected {len(df_full)} subject-session rows across {df_full.index.get_level_values('subid').nunique()} subjects")
print(df_full.head())

data_dir.mkdir(parents=True, exist_ok=True)
df_left.to_csv( data_dir / "left_volumes_long.csv")
df_right.to_csv(data_dir / "right_volumes_long.csv")
df_full.to_csv( data_dir / "full_volumes_long.csv")

logger.info("Done.")