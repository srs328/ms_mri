# %%
import pandas as pd
from pathlib import Path
import os
import nibabel as nib
import numpy as np
from tqdm import tqdm

from scipy import ndimage
from scipy.spatial import distance

#%%
hipsthomas_root = Path("/mnt/s/Data/srs-9/thalamus_project/data/sub1001-20170215")
dataproc_root = Path("/mnt/s/Data/srs-9/thalamus_project/data/sub1001-20170215")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")

thomL_img = nib.load(hipsthomas_root / "thomasfull_L.nii.gz").get_fdata()
thomR_img = nib.load(hipsthomas_root / "thomasfull_R.nii.gz").get_fdata()

# choroidL = nib.load(hipsthomas_root / "aseg-lv.nii.gz").get_fdata()
# choroidL_centroid = ndimage.center_of_mass(choroidL)

# choroidR = nib.load(hipsthomas_root / "aseg-rv.nii.gz").get_fdata()
# choroidR_centroid = ndimage.center_of_mass(choroidR)

lv_sdt = nib.load(hipsthomas_root / "aseg-lateral_ventricles_SDT.nii.gz").get_fdata()


# %% Left side

thom_inds = np.unique(thomL_img)
thom_inds = thom_inds[thom_inds > 0]
left_dists = []
all_dists = []
all_subjects = []
for ind in thom_inds:
    struct_pts = thomL_img.copy()
    struct_pts[thomL_img!=ind] = 0
    struct_pts[thomL_img==ind] = 1
    nonzero_coords = np.where(struct_pts == 1)
    min_dist = 10000
    for i in range(0, nonzero_coords[0]):
        dist = lv_sdt[*([coord[i]] for coord in nonzero_coords)]# left_dists.append()
        if dist < min_dist:
            min_dist = dist
    left_dists.append(min_dist)


# #%% Right side 

# thom_inds = np.unique(thomR_img)
# thom_inds = thom_inds[thom_inds > 0]
# right_dists = []
# all_dists = []
# all_subjects = []
# for ind in thom_inds:
#     struct_pts = thomR_img.copy()
#     struct_pts[thomR_img!=ind] = 0
#     struct_pts[thomR_img==ind] = 1
#     centroid = ndimage.center_of_mass(struct_pts)
#     # right_dists.append(distance.euclidean(centroid, choroidR_centroid))

# %%
df = pd.DataFrame({"left_exposure": left_dists}, index=[int(ind) for ind in thom_inds])
df.index.name = "index"
df.to_csv(data_file_dir / "mni_ventricle_shortestSDT_tmp.csv")

#     dists["ind"].append(ind)
#     dists["dist"].append(sdt[*centroid_round])

# df = pd.DataFrame(dists)
# df = df.set_index("ind")
# df.index.name = "struct"
# df.to_csv("mni-centroid-choroid_SDT.csv")