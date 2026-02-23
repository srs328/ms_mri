#!/usr/bin/env python3
"""

"""
# %%
import pandas as pd
from pathlib import Path
from mri_data import utils
from tqdm import tqdm

chacoroot = Path("/mnt/h/srs-9/chaco")
csv_path = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv")
subject_sessions = pd.read_csv(csv_path, index_col="sub")

hips_thomas_ref = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/hipsthomas_struct_index.csv", index_col="index"
)["struct"]

thalamic_nuclei = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
nuclei_labels = hips_thomas_ref[thalamic_nuclei].to_numpy()

# def main():
subject_data = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv",
    index_col="subid"
)
ms_subs = set(subject_data.index[subject_data["dz_type2"] == "MS"])

# %%
roi_means = []
for sub in tqdm(ms_subs, total=len(ms_subs)):
    ses = subject_sessions.loc[sub, "ses"]
    scan_dir = chacoroot / f"sub{sub}-{ses}"
    thomas_mask = scan_dir / "thomas_thalamus.nii.gz"
    chacovol = scan_dir / "chaco1/lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_mean.nii.gz"
    try:
        roi_means.append((sub, 
                        utils.compute_volume(chacovol, index_mask_file=thomas_mask, op_string="-M")))
    except Exception:
        continue

# %%
df = pd.DataFrame(roi_means, columns=["subid", "values"]).set_index("subid")
df = df["values"].apply(pd.Series).rename(columns=dict(enumerate(nuclei_labels)))
df.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/chaco1_roi_means.csv")