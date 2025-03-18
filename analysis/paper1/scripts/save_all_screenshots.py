import pandas as pd
from pathlib import Path
import subprocess
import sys
from mri_data import file_manager as fm

parent_path = "/home/srs-9/Projects/ms_mri/analysis/paper1"
sys.path.append(parent_path)
import helpers

drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
saveroot = drive_root / "srs-9/3Tpioneer_bids_images"
script = "/home/srs-9/Projects/ms_mri/analysis/paper1/scripts/save_screenshot.sh"

analysis_dir = Path("/home/srs-9/Projects/ms_mri/analysis")
df_full = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv", index_col="subid")
df_full = helpers.set_dz_type5(df_full)

coords_views = ["sagittal", "coronal", "axial"]
#! ⌄remember to edit all these⌄
save_subfolder = "pineal"
coords = [89, 110, 88]
viewport = "sagittal"
relevant_coord = coords[coords_views.index(viewport)]
save_suffix = f"-{relevant_coord}"
#! ^remember to edit all these^

#* Specify which subjects to take screenshots of
subs = [
    1548,
    1487,
    1328,
    1544,
    1487,
    1442,
    1066,
    1453,
    1248,
    1117,
    1001,
    1237,
    1158,
    1272,
    1518,
    1246,
    2027
]

# df_man = pd.read_csv(analysis_dir / "choroid_pineal2_pituitary_crosstrain_t1" / "dataframe.csv")
# subs = df_man['subid']
# df = df_full.loc[subs, :]
# df = df_full.loc[df_full['dz_type5'] == "PMS", :]

df = df_full.loc[subs, :]

for i, row in df.iterrows():
    t1_scan = dataroot / row['sub-ses'] / "proc/t1_std.nii.gz"
    t1_save = saveroot / save_subfolder / f"{i}-T1{save_suffix}.jpg"
    flair_scan = dataroot / row['sub-ses'] / "proc/flair_std.nii.gz"
    flair_save = saveroot / save_subfolder / f"{i}-FLAIR{save_suffix}.jpg"
    t1_gd_scan = dataroot / row['sub-ses'] / "proc/t1_gd_std.nii.gz"
    t1_gd_save = saveroot / save_subfolder / f"{i}-T1GD{save_suffix}.jpg"
    
    cmd_t1 = f"{script} {t1_scan} {viewport} {t1_save} {coords[0]} {coords[1]} {coords[2]}"
    if not t1_save.is_file():
        print(cmd_t1)
        subprocess.run(cmd_t1.split(" "))

    cmd_flair = f"{script} {flair_scan} {viewport} {flair_save} {coords[0]} {coords[1]} {coords[2]}"
    if not flair_save.is_file():
        print(cmd_flair)
        subprocess.run(cmd_flair.split(" "))

    cmd_t1_gd = f"{script} {t1_gd_scan} {viewport} {t1_gd_save} {coords[0]} {coords[1]} {coords[2]}"
    if not t1_gd_save.is_file():
        print(cmd_t1_gd)
        subprocess.run(cmd_t1_gd.split(" "))
