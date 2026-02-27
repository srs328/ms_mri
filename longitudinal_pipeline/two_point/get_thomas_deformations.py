# %%
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path
from loguru import logger
import sys

import subprocess 

# # %%

# now = datetime.now()
# log_filename = now.strftime(
#     f"{os.path.basename(__file__).split('.')[0]}-%Y%m%d_T%H%M%S.log"
# )
# logger.remove()
# logger.add(log_filename, mode="w")



# %%
subject_sessions = pd.read_csv("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
# subject_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")

# # dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
# dataroot = Path("/home/srs-9/hpc/data/longitudinal")
# data_dir = Path("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/data0")

subid = sys.argv[1]
dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
# dataroot = Path("/home/srs-9/hpc/data/longitudinal")

KEY_REF = [
    "1-THALAMUS.nii.gz",
"10-MGN.nii.gz",
"11-CM.nii.gz",
"12-MD-Pf.nii.gz",
"13-Hb.nii.gz",
"14-MTT.nii.gz",
"2-AV.nii.gz",
"26-Acc.nii.gz",
"27-Cau.nii.gz",
"28-Cla.nii.gz",
"29-GPe.nii.gz",
"30-GPi.nii.gz",
"31-Put.nii.gz",
"32-RN.nii.gz",
"33-GP.nii.gz",
"34-Amy.nii.gz",
"4-VA.nii.gz",
"4567-VL.nii.gz",
"5-VLa.nii.gz",
"6-VLP.nii.gz",
"6_VLPd.nii.gz",
"6_VLPv.nii.gz",
"7-VPL.nii.gz",
"8-Pul.nii.gz",
"9-LGN.nii.gz",
"CL_L.nii.gz",
]

def fslstats(mask_file, stat_flags, index_mask=None):
    """
    Run fslstats and return results as a list of floats.
    
    Parameters
    ----------
    mask_file : str
        Path to the input image
    stat_flags : str or list
        Stats flags e.g. '-M' or ['-M', '-S']
    index_mask : str, optional
        Path to index mask file (for -K option)
    
    Returns
    -------
    list of float (single stat) or list of lists (multiple stats per label)
    """
    if isinstance(stat_flags, str):
        stat_flags = stat_flags.split()
    
    cmd = ['fslstats']
    if index_mask:
        cmd += ['-K', index_mask]
    cmd += [mask_file] + stat_flags
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    
    parsed = []
    for line in lines:
        values = [float(v) for v in line.split()]
        parsed.append(values[0] if len(values) == 1 else values)
    
    return parsed


# %%

ses1 = subject_sessions.loc[subid, 'ses1']
ses2 = subject_sessions.loc[subid, 'ses2']
group_dir = dataroot / f"sub{subid}/group"

if not (group_dir / "bilateral" / "thomas_posterior.nii.gz").exists():
    subprocess.run(["combineNuclei.sh", group_dir])

ses1_jac = group_dir / f"sub{subid}_input0000-t1_brain_wmn_{ses1}-1Warp-Jacobian00.nii.gz"
ses2_jac = group_dir / f"sub{subid}_input0001-t1_brain_wmn_{ses2}-1Warp-Jacobian00.nii.gz"

thomas_left_dir = group_dir / "left"
thoams_right_dir = group_dir / "right"
thoams_full_dir = group_dir / "bilateral"

left_defs = []
right_defs = []
full_defs = []
for mask_file in KEY_REF:
    print(mask_file)
    left_mask_path = thomas_left_dir / mask_file
    right_mask_path = thoams_right_dir / mask_file
    full_mask_path = thoams_full_dir / mask_file

    def1_left = fslstats(ses1_jac, "-M", index_mask=left_mask_path)
    def2_left = fslstats(ses2_jac, "-M", index_mask=left_mask_path)
    left_defs.append((mask_file.removesuffix(".nii.gz"), def1_left[0], def2_left[0]))

    def1_right = fslstats(ses1_jac, "-M", index_mask=right_mask_path)
    def2_right = fslstats(ses2_jac, "-M", index_mask=right_mask_path)

    right_defs.append((mask_file.removesuffix(".nii.gz"), def1_right[0], def2_right[0]))

    def1_full = fslstats(ses1_jac, "-M", index_mask=full_mask_path)
    def2_full = fslstats(ses2_jac, "-M", index_mask=full_mask_path)
    full_defs.append((mask_file.removesuffix(".nii.gz"), def1_full[0], def2_full[0]))

# %%
df_full = pd.DataFrame(full_defs, columns=["struct", "ses1", "ses2"])
