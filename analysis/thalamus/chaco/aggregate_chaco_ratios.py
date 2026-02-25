#!/usr/bin/env python3
"""

"""
# %%
import pandas as pd
from pathlib import Path
from mri_data import utils
import subprocess
from tqdm import tqdm

# %%

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

chacoroot = Path("/mnt/h/srs-9/chaco")
csv_path = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv")
subject_sessions = pd.read_csv(csv_path, index_col="sub")

hips_thomas_ref = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/hipsthomas_struct_index.csv", index_col="index"
)["struct"]

thalamic_nuclei = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
nuclei_labels = hips_thomas_ref[thalamic_nuclei].to_list()
nuclei_labels.extend(["anterior", "ventral", "posterior", "medial"])

# def main():
subject_data = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv",
    index_col="subid"
)
ms_subs = set(subject_data.index[subject_data["dz_type2"] == "MS"])
script_file = "combineNuclei.sh"

# %%
roi_means = []
for sub in tqdm(ms_subs, total=len(ms_subs)):
    ses = subject_sessions.loc[sub, "ses"]
    scan_dir = chacoroot / f"sub{sub}-{ses}"
    try:
        subprocess.run(["bash", script_file, str(scan_dir)], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print(f"sub{sub}: Failed on combining nuclei")
        
    chacovol = scan_dir / "chaco1/lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_mean.nii.gz"
    thomas_mask = scan_dir / "thomas_thalamus.nii.gz"
    ventral_mask = scan_dir / "thomas_ventral.nii.gz"
    anterior_mask = scan_dir / "thomas_anterior.nii.gz"
    posterior_mask = scan_dir / "thomas_posterior.nii.gz"
    medial_mask = scan_dir / "thomas_medial.nii.gz"
    try:
        # means = utils.compute_volume(chacovol, index_mask_file=thomas_mask, op_string="-M")
        means = fslstats(chacovol, "-M", thomas_mask)
    except Exception:
        continue
    try:
        # combined_means = utils.compute_volume(chacovol, index_mask_file=anterior_mask, op_string="-M")
        combined_means = fslstats(chacovol, "-M", anterior_mask)
        combined_means.extend(fslstats(chacovol, "-M", ventral_mask))
        combined_means.extend(fslstats(chacovol, "-M", posterior_mask))
        combined_means.extend(fslstats(chacovol, "-M", medial_mask))
    except Exception:
        means.extend([None, None, None, None])
    else:
        means.extend(combined_means)
    roi_means.append((sub, means))

# %%
df = pd.DataFrame(roi_means, columns=["subid", "values"]).set_index("subid")
df = df["values"].apply(pd.Series).rename(columns=dict(enumerate(nuclei_labels)))
df.to_csv("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/chaco1_roi_means2.csv")