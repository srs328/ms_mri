import pandas as pd
from pathlib import Path
import os
import shutil

dataroot = Path("/media/smbshare/3Tpioneer_bids")
ascho_dataroot = Path("/media/smbshare/srs-9/aschoplex/test2")
curr_dir = os.path.abspath(__file__)
subjects_file = "/home/srs-9/Projects/ms_mri/analysis/paper1/data0/manual_labels.csv"
df = pd.read_csv(subjects_file, index_col="subid")

ft_subs = [
    1011,
    1019,
    1029,
    1037,
    1038,
    1080,
    1085,
    1087,
    1089,
    1109,
    1152,
    1163,
    1188,
    1191,
    1234,
    1265,
    1272,
    1280,
    1293,
    1321,
    1355,
    1498,
    1518,
    1540,
    1548,
    2083,
    2097,
    2132,
    2144,
    2164
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


#python $ASCHOPLEXDIR/launching_tool.py --dataroot /media/smbshare/srs-9/aschoplex/test1 --work_dir /media/smbshare/srs-9/aschoplex/test1/work_dir/ --finetune yes --predict yes