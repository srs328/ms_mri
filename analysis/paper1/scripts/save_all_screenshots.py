import pandas as pd
from pathlib import Path
import subprocess
import sys

parent_path = "/home/srs-9/Projects/ms_mri/analysis/paper1"
sys.path.append(parent_path)
import helpers

# coords [sag, cor, ax]
coords = [91, 110, 88]
viewport = "axial"
save_suffix = "-92"
#! remember to edit this
save_subfolder = "choroid"

analysis_dir = Path("/home/srs-9/Projects/ms_mri/analysis")
df_full = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv", index_col="subid")
df_full = helpers.set_dz_type5(df_full)
#* Specify which subjects to take screenshots of 
# df_man = pd.read_csv(analysis_dir / "choroid_pineal2_pituitary_crosstrain_t1" / "dataframe.csv")
# man_subs = df_man['subid']
# df = df_full.loc[man_subs, :]
df = df_full.loc[df_full['dz_type5'] == "PMS", :]


dataroot = Path("/media/smbshare/3Tpioneer_bids")
saveroot = Path("/media/smbshare/srs-9/3Tpioneer_bids_images")

script = "/home/srs-9/Projects/ms_mri/analysis/paper1/scripts/save_screenshot.sh"


for i, row in df.iterrows():
    t1_scan = dataroot / row['sub-ses'] / "proc/t1_std.nii.gz"
    t1_save = saveroot / save_subfolder / f"{i}-T1{save_suffix}.jpg"
    flair_scan = dataroot / row['sub-ses'] / "proc/flair-brain-mni_reg.nii.gz"
    flair_save = saveroot / save_subfolder / f"{i}-FLAIR{save_suffix}.jpg"
    
    cmd_t1 = f"{script} {t1_scan} {viewport} {t1_save} {coords[0]} {coords[1]} {coords[2]}"
    if not t1_save.is_file():
        print(cmd_t1)
        subprocess.run(cmd_t1.split(" "))

    cmd_flair = f"{script} {flair_scan} {viewport} {flair_save} {coords[0]} {coords[1]} {coords[2]}"
    if not flair_save.is_file():
        print(cmd_flair)
        subprocess.run(cmd_flair.split(" "))
