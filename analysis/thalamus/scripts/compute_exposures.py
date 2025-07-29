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
hipsthomas_root = Path("/mnt/h/srs-9/hipsthomas")
dataproc_root = Path("/mnt/h/srs-9/thalamus_project/data0")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")

subject_sessions = pd.read_csv(data_file_dir / "subject-sessions.csv")

which_distance = "ventricle"


# %%
def load_choroid_sdt(root, sub, ses):
    file = os.path.join(root, f"sub{sub}-{ses}", "choroid-sdt.nii.gz")
    return nib.load(file).get_fdata()


def load_ventricle_sdt(root, sub, ses):
    file = os.path.join(root, f"sub{sub}-{ses}", "aseg-rv-fix-sdt.nii.gz")
    return nib.load(file).get_fdata()


def load_thomas0(root, sub, ses):
    thomas_dir = root / f"sub{sub}-{ses}"
    thomL_file = thomas_dir / "left/thomasfull_L.nii.gz"
    thomL_img = nib.load(thomL_file)
    thomR_file = thomas_dir / "right/thomasfull_R.nii.gz"
    thomR_img = nib.load(thomR_file)
    return thomL_img, thomR_img


def load_thomas(root, sub, ses):
    thomas_dir = root / f"sub{sub}-{ses}"
    thomL_file = thomas_dir / "thomasfull_R.nii.gz"
    thomL_img = nib.load(thomL_file)
    thomR_file = thomas_dir / "thomasfull_R.nii.gz"
    # thomR_img = nib.load(thomR_file)
    thomR_img = None
    return thomL_img, thomR_img


def load_file(root, sub, ses, file):
    thomas_dir = root / f"sub{sub}-{ses}"
    thom_img = nib.load(thomas_dir / "left" / file)
    return thom_img


distance_metrics = {"choroid": load_choroid_sdt, "ventricle": load_ventricle_sdt}
save_names = {
    "choroid": "centroid-choroid_SDTX.csv",
    "ventricle": "centroid-ventricle_SDT_fixed-right.csv",
}
load_function = distance_metrics[which_distance]
save_name = save_names[which_distance]

# %% [markdown]
## Centroid-SDT metric

# %%
all_dists = []
all_subjects = []
for i, row in tqdm(subject_sessions.iterrows(), total=len(subject_sessions)):
    sub = row["sub"]
    ses = row["ses"]
    try:
        sdt = load_function(dataproc_root, sub, ses)
        thomL_img, _ = load_thomas(dataproc_root, sub, ses)
        thom = thomL_img.get_fdata()
        thom_inds = np.unique(thom)
        thom_inds = thom_inds[thom_inds > 0]
        dists = {}
        for ind in thom_inds:
            struct_pts = thom.copy()
            struct_pts[thom != ind] = 0
            struct_pts[thom == ind] = 1
            centroid = ndimage.center_of_mass(struct_pts)
            centroid_round = [int(cent) for cent in centroid]
            dists[int(ind)] = sdt[*centroid_round]

        # for ind, file in [
        #     (1, "1-THALAMUS.nii.gz"),
        #     (33, "33-GP.nii.gz"),
        #     (34, "34-Amy.nii.gz"),
        # ]:
        #     thom_img = load_file(dataproc_root, sub, ses, file)
        #     struct_pts = thom_img.get_fdata()
        #     centroid = ndimage.center_of_mass(struct_pts)
        #     centroid_round = [int(cent) for cent in centroid]
        #     dists[int(ind)] = sdt[*centroid_round]

        all_dists.append(dists)
        all_subjects.append(sub)

    except Exception as e:
        print(e)
        continue


# %%

df = pd.DataFrame(all_dists, index=all_subjects)
df.to_csv(data_file_dir / save_name)

# %%

# for i, row in subject_sessions.iterrows():
#     sub = row['sub']
#     ses = row['ses']
#     file = os.path.join(dataproc_root, f"sub{sub}-{ses}", "aseg-ventricles-sdt.nii.gz")
#     if not os.path.exists(file):
#         print(sub)
# try:
#     sdt = load_function(dataproc_root, sub, ses)
# except FileNotFoundError:
#     print(sub)
#     continue

# # %% [markdown]
# ## Ventricle-SDT metric
# # %%

# # subject_sessions.set_index("sub", inplace=True)
# # 1326
# subjects = [1326, 2195, 1076, 1042, 1508, 1071, 1241, 1003, 1301, 1001, 1107, 1125, 1161, 1198, 1218, 1527, 1376, 2075, 1023, 1038, 1098]
# all_dists = []
# all_subjects = []
# for sub in subjects:
#     ses = subject_sessions.loc[sub, 'ses']
#     try:
#         ventricle_sdt = load_ventricle_sdt(hipsthomas_root, sub, ses)
#         thomL_img, _ = load_thomas(hipsthomas_root, sub, ses)
#         thom = thomL_img.get_fdata()
#         thom_inds = np.unique(thom)
#         thom_inds = thom_inds[thom_inds > 0]
#         dists = {}
#         for ind in thom_inds:
#             struct_pts = thom.copy()
#             struct_pts[thom!=ind] = 0
#             struct_pts[thom==ind] = 1
#             centroid = ndimage.center_of_mass(struct_pts)
#             centroid_round = [int(cent) for cent in centroid]
#             dists[int(ind)] = ventricle_sdt[*centroid_round]

#         all_dists.append(dists)
#         all_subjects.append(sub)

#     except Exception as e:
#         print(e)
#         continue

# # %%

# df = pd.DataFrame(all_dists, index=all_subjects)
# df.index.name="subid"
# df.to_csv(data_file_dir / "ventricle-SDT.csv")
