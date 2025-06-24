# %%
import pandas as pd
from pathlib import Path
import os
import nibabel as nib
import numpy as np
from tqdm.notebook import tqdm

from scipy import ndimage
from scipy.spatial import distance

#%%

dataproc_root = Path("/mnt/h/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")

subject_sessions = pd.read_csv(data_file_dir / "subject-sessions.csv")

save_name = "centroid-choroid_centroid"

#%%

def load_thomas(root, sub, ses):
    thomas_dir = root / f"sub{sub}-{ses}"
    thomL_file = thomas_dir / "thomasfull_L.nii.gz"
    thomL_img = nib.load(thomL_file).get_fdata()
    thomR_file = thomas_dir / "thomasfull_R.nii.gz"
    thomR_img = nib.load(thomR_file).get_fdata()
    return thomL_img, None

#%%

all_left_dists = []
all_right_dists = []
all_subjects = []

for i, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    sub = row['sub']
    ses = row['ses']
    try:
        subject_root = dataproc_root / f"sub{sub}-{ses}"
        choroid_left = nib.load(subject_root / "choroid_left.nii.gz").get_fdata()
        # choroid_right = nib.load(subject_root / "choroid_right.nii.gz").get_fdata()
        choroid_left_centroid = ndimage.center_of_mass(choroid_left)
        # choroid_right_centroid = ndimage.center_of_mass(choroid_right)
        thomL, thomR = load_thomas(dataproc_root, sub, ses)

        # left side
        thom = thomL
        thom_inds = np.unique(thom)
        thom_inds = thom_inds[thom_inds > 0]
        left_dists = {}
        for ind in thom_inds:
            struct_pts = thom.copy()
            struct_pts[thom!=ind] = 0
            struct_pts[thom==ind] = 1
            centroid = ndimage.center_of_mass(struct_pts)
            left_dists[int(ind)] = distance.euclidean(centroid, choroid_left_centroid)

        # right side
        # thom = thomR
        # thom_inds = np.unique(thom)
        # thom_inds = thom_inds[thom_inds > 0]
        # right_dists = {}
        # for ind in thom_inds:
        #     struct_pts = thom.copy()
        #     struct_pts[thom!=ind] = 0
        #     struct_pts[thom==ind] = 1
        #     centroid = ndimage.center_of_mass(struct_pts)
        #     right_dists[int(ind)] = distance.euclidean(centroid, choroid_right_centroid)
        
        # for ind, file in [(1, "1-THALAMUS.nii.gz"), (33, "33-GP.nii.gz"), (34, "34-Amy.nii.gz")]:
        #     thom_img = load_file(hipsthomas_root, sub, ses, file)
        #     struct_pts = thom_img.get_fdata()
        #     centroid = ndimage.center_of_mass(struct_pts)
        #     dists[int(ind)] = distance.euclidean(centroid, choroid_centroid)
        
        all_left_dists.append(left_dists)
        # all_right_dists.append(right_dists)
        all_subjects.append(sub)
    
    except Exception as e:
        print(e)
        continue

# %%

left_name = f"{save_name}-left.csv"
right_name = f"{save_name}-right.csv"

df_left = pd.DataFrame(all_left_dists, index=all_subjects)
df_left.index.name = "subid"
df_left.to_csv(data_file_dir / left_name)

# df_right = pd.DataFrame(all_right_dists, index=all_subjects)
# df_right.index.name = "subid"
# df_right.to_csv(data_file_dir / right_name)

