import pandas as pd
from pathlib import Path
import os
import shutil
from tqdm import tqdm

dataroot = Path("/media/smbshare/3Tpioneer_bids")
ascho_dataroot = Path("/media/smbshare/srs-9/aschoplex/test1")
curr_dir = os.path.abspath(__file__)
subjects_file = "/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv"
df = pd.read_csv(subjects_file, index_col="subid")

# inf_subs = [
#     1453,
#     1248,
#     1066,
#     1117,
#     1442
# ]

inf_subs = []
for i, row in df.iterrows():
    if not isinstance(row['label_folder'], str):
        continue
    if "3Tpioneer_bids_predictions" in row['label_folder']:
        inf_subs.append(i)

for sub in tqdm(inf_subs, total=len(inf_subs)):
    sub_root = dataroot / df.loc[sub, "sub-ses"]
    image = sub_root / "t1.nii.gz"
    if not image.is_file():
        raise FileNotFoundError(f"sub-{sub} t1.nii.gz not found")
    
    image_svname = f"MRI_{sub}_image.nii.gz"
    image_svpath = ascho_dataroot / "image_Ts" / image_svname

    if not image_svpath.exists():
        shutil.copyfile(image, image_svpath)

#  python $ASCHOPLEXDIR/launching_tool.py --dataroot /media/smbshare/srs-9/aschoplex/test1 --work_dir /media/smbshare/srs-9/aschoplex/test1/work_dir --finetune no --prediction ft