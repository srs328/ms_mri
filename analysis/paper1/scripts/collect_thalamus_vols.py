import os
import re
from pathlib import Path
import pandas as pd
from mri_data import utils
from tqdm import tqdm

hips_thomas_home = Path("/media/smbshare/srs-9/thalamus_seg/hipsthomas_out")
logdir = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/scripts/logs")
data_dir = Path("/home/srs-9/Projects/ms_mri/analysis/paper1/data0")

all_vols = []
subjects = []
no_hips_thomas = []
failed_hips_thomas = []
for folder in tqdm(hips_thomas_home.iterdir()):
    if not folder.is_dir():
        continue
    subject = int(re.match(r"sub(\d{4})", folder.name)[1])
    try:
        vols = utils.get_hipsthomas_vols(folder)
    except FileNotFoundError:
        no_hips_thomas.append(subject)
        continue
    except Exception:
        failed_hips_thomas.append(subject)

    all_vols.append(vols)
    subjects.append(subject)

df = pd.DataFrame(all_vols, index=subjects)
df.to_csv(data_dir / "hipsthomas_vols.csv", index_label="subid")

with open(logdir / "no_hipsthomas.txt", 'w') as f:
    for line in no_hips_thomas:
        f.write(f"{line}\n")

with open(logdir / "failed_hipsthomas.txt", 'w') as f:
    for line in failed_hips_thomas:
        f.write(f"{line}\n")
        