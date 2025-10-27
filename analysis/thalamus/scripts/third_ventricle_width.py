import nibabel as nib
import numpy as np
import cv2
from skimage import measure
from scipy.spatial import ConvexHull
from feret_diameter import get_min_max_feret_from_mask
import json
from pathlib import Path
from tqdm import tqdm
import pandas as pd


def get_width(filepath):
    img = nib.load(filepath)
    data = img.get_fdata()
    vox = img.header.get_zooms()
    aff = img.affine

    widths = []
    for y in range(data.shape[1]):  # coronal slices
        slice_mask = data[:, y, :].astype('uint8')
        if len(np.where(slice_mask > 0)[0]) > 1:
            min_feret, max_feret = get_min_max_feret_from_mask(slice_mask)
            widths.append(min_feret*vox[0])  # in mm

    return max(widths)


third_ventricle_name = "aseg-third_ventricle.nii.gz"
with open("/home/srs-9/Projects/ms_mri/data/subject-sessions-longit.json", 'r') as f:
    subject_sessions = json.load(f)

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")

width_data = {'subid': [], 'third_ventricle_width': []}
for subid in tqdm(subject_sessions, total=len(subject_sessions)):
    width_data['subid'].append(int(subid))
    sessions = sorted(subject_sessions[subid])
    sesid = sessions[0]

    data_dir = dataroot / f"sub{subid}-{sesid}"
    third_ventricle_file = data_dir / third_ventricle_name
    try:
        max_width = get_width(third_ventricle_file)
    except Exception as e:
        print(subid, e)
        max_width = None
    width_data['third_ventricle_width'].append(max_width)

df = pd.DataFrame(width_data)
df.set_index('subid', inplace=True)
df.index.name = "subid"

df.to_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/third_ventricle_width.csv"
)