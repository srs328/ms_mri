# %%
import pandas as pd
from pathlib import Path
import os
import nibabel as nib
import numpy as np
from tqdm import tqdm

from scipy import ndimage
from scipy.spatial import distance

hipsthomas_root = Path("/media/smbshare/srs-9/hipsthomas")
dataproc_root = Path("/media/smbshare/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")

thomL_img = nib.load(hipsthomas_root / "MNI152_T1_1mm/left/thomasfull_L.nii.gz")
sdt = nib.load(dataproc_root / "MNI152_T1_1mm/choroid-sdt.nii.gz").get_fdata()

thom = thomL_img.get_fdata()
thom_inds = np.unique(thom)
thom_inds = thom_inds[thom_inds > 0]
# dists = {"ind": [], "dist": []}
dists = {}
all_dists = []
all_subjects = []
for ind in thom_inds:
    struct_pts = thom.copy()
    struct_pts[thom!=ind] = 0
    struct_pts[thom==ind] = 1
    centroid = ndimage.center_of_mass(struct_pts)
    centroid_round = [int(cent) for cent in centroid]
    dists[int(ind)] = sdt[*centroid_round]


# %%
df = pd.DataFrame(dists, index=[0])
df.to_csv("mni-centroid-choroid_SDT2.csv")

#     dists["ind"].append(ind)
#     dists["dist"].append(sdt[*centroid_round])

# df = pd.DataFrame(dists)
# df = df.set_index("ind")
# df.index.name = "struct"
# df.to_csv("mni-centroid-choroid_SDT.csv")