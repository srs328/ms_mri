import os
import re
from pathlib import Path
import pandas as pd
from mri_data import utils
from tqdm import tqdm
import csv

hips_thomas_home = Path("/media/smbshare/srs-9/hipsthomas")
logdir = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/scripts/logs")
data_dir = Path("/home/srs-9/Projects/ms_mri/data")
assert data_dir.exists()

def parse_hipsthomas_vols(file):
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=" ")
        vols = {row[0]: float(row[1]) for row in reader}
    return vols


def get_hipsthomas_vols(loc):
    left_vols = parse_hipsthomas_vols(os.path.join(loc, "left", "nucleiVols.txt"))
    right_vols = parse_hipsthomas_vols(os.path.join(loc, "right", "nucleiVols.txt"))
    # vols = {key: left_vols[key] + right_vols[key] for key in left_vols}
    return left_vols, right_vols

all_vols = []
all_left_vols = []
all_right_vols = []
subjects = []
no_hips_thomas = []
failed_hips_thomas = []
for folder in tqdm(hips_thomas_home.iterdir()):
    if not folder.is_dir():
        continue
    subject = int(re.match(r"sub(\d{4})", folder.name)[1])
    try:
        left_vols, right_vols = get_hipsthomas_vols(folder)
    except FileNotFoundError:
        no_hips_thomas.append(subject)
        continue
    except Exception:
        failed_hips_thomas.append(subject)

    vols = {key: left_vols[key] + right_vols[key] for key in left_vols}

    all_vols.append(vols)
    all_left_vols.append(left_vols)
    all_right_vols.append(right_vols)
    subjects.append(subject)

df = pd.DataFrame(all_vols, index=subjects)
df.to_csv(data_dir / "hipsthomas_vols.csv", index_label="subid")

df_left = pd.DataFrame(all_left_vols, index=subjects)
df_left.to_csv(data_dir / "hipsthomas_left_vols.csv", index_label="subid")

df_right = pd.DataFrame(all_right_vols, index=subjects)
df_right.to_csv(data_dir / "hipsthomas_right_vols.csv", index_label="subid")

with open(logdir / "no_hipsthomas.txt", 'w') as f:
    for line in no_hips_thomas:
        f.write(f"{line}\n")

with open(logdir / "failed_hipsthomas.txt", 'w') as f:
    for line in failed_hips_thomas:
        f.write(f"{line}\n")
        