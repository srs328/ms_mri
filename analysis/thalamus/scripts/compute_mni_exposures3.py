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
hipsthomas_root = Path("/mnt/h/srs-9/hips-thomas/MNI152_T1_1mm")
dataproc_root = Path("/mnt/h/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")

thomL_img = nib.load(hipsthomas_root / "left/thomasfull_L.nii.gz").get_fdata()
thomR_img = nib.load(hipsthomas_root / "right/thomasfull_R.nii.gz").get_fdata()

choroidL = nib.load(hipsthomas_root / "choroid_left.nii.gz").get_fdata()
choroidL_centroid = ndimage.center_of_mass(choroidL)

choroidR = nib.load(hipsthomas_root / "choroid_right.nii.gz").get_fdata()
choroidR_centroid = ndimage.center_of_mass(choroidR)


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
    centroid = ndimage.center_of_mass(struct_pts)
    left_dists.append(distance.euclidean(centroid, choroidL_centroid))


#%% Right side 

thom_inds = np.unique(thomR_img)
thom_inds = thom_inds[thom_inds > 0]
right_dists = []
all_dists = []
all_subjects = []
for ind in thom_inds:
    struct_pts = thomR_img.copy()
    struct_pts[thomR_img!=ind] = 0
    struct_pts[thomR_img==ind] = 1
    centroid = ndimage.center_of_mass(struct_pts)
    right_dists.append(distance.euclidean(centroid, choroidR_centroid))

# %%
df = pd.DataFrame({"left_exposure": left_dists, "right_exposures": right_dists}, index=[int(ind) for ind in thom_inds])
df.index.name = "index"
df.to_csv(data_file_dir / "mni_centroid_centroid_dists.csv")

#     dists["ind"].append(ind)
#     dists["dist"].append(sdt[*centroid_round])

# df = pd.DataFrame(dists)
# df = df.set_index("ind")
# df.index.name = "struct"
# df.to_csv("mni-centroid-choroid_SDT.csv")


# medial_centroid = ndimage.center_of_mass(medial)
# ventral_centroid = ndimage.center_of_mass(ventral)
# posterior_centroid = ndimage.center_of_mass(posterior)
# anterior_centroid = ndimage.center_of_mass(anterior)