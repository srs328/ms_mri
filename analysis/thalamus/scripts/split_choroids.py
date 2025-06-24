#%%

from nipype.interfaces.freesurfer.utils import ImageInfo
from pathlib import Path
import subprocess
import os
from tqdm.notebook import tqdm

#%%

data_dir = Path("/media/smbshare/srs-9/thalamus_project/data")
folders = [Path(item) for item in os.scandir(data_dir) if item.is_dir() and "sub" in item.name]

make_mask_script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/scripts/create_right_mask.sh"
# %%

# for folder in tqdm(folders, total=len(folders)):
for folder in [Path("/media/smbshare/srs-9/thalamus_project/data/sub1064-20170310")]:
    # print(folder.name)
    if not (folder / "choroid.nii.gz").exists():
        continue
    choroid = folder / "choroid.nii.gz"
    left_choroid = folder / "choroid_left.nii.gz"
    right_choroid = folder / "choroid_right.nii.gz"
    in_file = folder / "t1.nii.gz"
    left_mask = folder / "left_mask.nii.gz"
    right_mask = folder / "right_mask.nii.gz"

    if not right_mask.exists():
        info = ImageInfo()
        info.inputs.in_file = in_file
        result = info.run()
        halfx = result.outputs.dimensions[0] / 2
        subprocess.run([make_mask_script, in_file, str(halfx), right_mask])
    if not left_mask.exists():
        subprocess.run(["fslmaths", right_mask, "-binv", left_mask])
    if not left_choroid.exists():
        subprocess.run(["fslmaths", choroid, "-mas", right_mask, left_choroid])
        print(folder.name, "Left")
    if not right_choroid.exists():
        print(folder.name, "Right")
        subprocess.run(["fslmaths", choroid, "-mas", left_mask, right_choroid])
