# %%
import pandas as pd
from pathlib import Path
import os
import nibabel as nib
import numpy as np
from tqdm import tqdm

from scipy import ndimage
from scipy.spatial import distance

# %%
hipsthomas_root = Path("/media/smbshare/srs-9/hipsthomas")
dataproc_root = Path("/media/smbshare/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")

subject_sessions = pd.read_csv(data_file_dir / "subject-sessions.csv", names=["sub", "ses"], header=None)

# %%
def load_choroid_sdt(root, sub, ses):
    file = os.path.join(root, f"sub{sub}-{ses}", "choroid-sdt.nii.gz")
    return nib.load(file).get_fdata()

def load_thomas(root, sub, ses):
    thomas_dir = root / f"sub{sub}-{ses}"
    thomL_file = thomas_dir / "left/thomasfull_L.nii.gz"
    thomL_img = nib.load(thomL_file)
    thomR_file = thomas_dir / "right/thomasfull_R.nii.gz"
    thomR_img = nib.load(thomR_file)
    return thomL_img, thomR_img

# %% [markdown]
# Centroid-SDT metric

# %%
all_dists = []
all_subjects = []
for i, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    sub = row['sub']
    ses = row['ses']
    try:
        choroid_sdt = load_choroid_sdt(dataproc_root, sub, ses)
        thomL_img, _ = load_thomas(hipsthomas_root, sub, ses)
        thom = thomL_img.get_fdata()
        thom_inds = np.unique(thom)
        thom_inds = thom_inds[thom_inds > 0]
        dists = {}
        for ind in thom_inds:
            struct_pts = thom.copy()
            struct_pts[thom!=ind] = 0
            struct_pts[thom==ind] = 1
            centroid = ndimage.center_of_mass(struct_pts)
            centroid_round = [int(cent) for cent in centroid]
            dists[int(ind)] = choroid_sdt[*centroid_round]
        
        all_dists.append(dists)
        all_subjects.append(sub)
    
    except Exception as e:
        print(e)
        continue


# %%

df = pd.DataFrame(all_dists, index=all_subjects)
df.to_csv(data_file_dir / "centroid-SDT.csv")