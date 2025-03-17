import pandas as pd
from pathlib import Path
import os
import shutil

dataroot = Path("/mnt/h/3Tpioneer_bids")
ascho_dataroot = Path("/mnt/h/srs-9/aschoplex/test1")
curr_dir = os.path.abspath(__file__)
subjects_file = "/home/srs-9/Projects/ms_mri/analysis/paper1/data0/manual_labels.csv"
df = pd.read_csv(subjects_file, index_col="subid")

ft_subs = [
    1010,
    1019,
    2146,
    2097,
    1498,
    1355,
    1038,
    1152,
    1188,
    1259,
]

pred_subs = df.loc[~(df.index.isin(ft_subs)), :].index.tolist()

for sub in ft_subs:
    sub_root = dataroot / df.loc[sub, "sub-ses"]
    image = sub_root / "t1.nii.gz"
    if not image.is_file():
        raise FileNotFoundError(f"sub-{sub} t1.nii.gz not found")
    label = sub_root / "choroid_t1_flair-CH.nii.gz"
    if not label.is_file():
        label = sub_root / "choroid_t1_flair-ED.nii.gz"
        if not label.is_file():
            raise FileNotFoundError(f"sub-{sub} choroid label not found")
    
    image_svname = f"MRI_{sub}_image.nii.gz"
    image_svpath = ascho_dataroot / "image_Tr" / image_svname
    label_svname = f"MRI_{sub}_seg.nii.gz"
    label_svpath = ascho_dataroot / "label_Tr" / label_svname

    if not image_svpath.exists():
        shutil.copyfile(image, image_svpath)
    if not label_svpath.exists():
        shutil.copyfile(label, label_svpath)


for sub in pred_subs:
    sub_root = dataroot / df.loc[sub, "sub-ses"]
    image = sub_root / "t1.nii.gz"
    if not image.is_file():
        raise FileNotFoundError(f"sub-{sub} t1.nii.gz not found")
    
    image_svname = f"MRI_{sub}_image.nii.gz"
    image_svpath = ascho_dataroot / "image_Ts" / image_svname

    if not image_svpath.exists():
        shutil.copyfile(image, image_svpath)


#python $ASCHOPLEXDIR/launching_tool.py --dataroot /mnt/h/srs-9/aschoplex/test1 --work_dir /mnt/h/srs-9/aschoplex/test1/work_dir/ --finetune yes --predict yes