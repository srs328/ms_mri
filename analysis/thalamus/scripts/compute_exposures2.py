#%%
from pathlib import Path
import nibabel as nib
import subprocess
import os
import re
from nipype.interfaces import fsl
from tqdm.notebook import tqdm
import pandas as pd

#%%

#! Pre steps that I did in terminal:
#   Created left and right hemisphere mask with instructions (https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=fsl;e4c252f3.1406) to split choroid into left and right

work_dir = Path("/media/smbshare/srs-9/hipsthomas/MNI152_T1_1mm")

file_items = [item.name for item in os.scandir(work_dir/"left") if item.is_file()]
file_names = []
for item in file_items:
    if re.match(r"\d+-.+(?<!_sdt)\.nii\.gz", item):
        file_names.append(item)

#%%

for name in file_names:
    filepath = work_dir / "left" / name
    filestem = filepath.stem.split(".")[0]

    cmd = ["c3d", filepath, "-sdt", "-o", work_dir / "left" / f"{filestem}_sdt.nii.gz"]
    subprocess.run(cmd)

    filepath = work_dir / "right" / name
    cmd = ["c3d", filepath, "-sdt", "-o", work_dir / "right" / f"{filestem}_sdt.nii.gz"]
    subprocess.run(cmd)

#%%

left_exposures = []
right_exposures = []
for item in tqdm(file_names, total=len(file_names)):
    struct_stem = item.split(".")[0]
    for side in ["left", "right"]:
        mask_file = work_dir / side / f"{struct_stem}.nii.gz"
        sdt_file = work_dir / f"choroid_{side}_sdt.nii.gz"

        stats1 = fsl.ImageStats()
        stats1.inputs.index_mask_file = mask_file
        stats1.inputs.in_file = sdt_file
        stats1.inputs.op_string = "-M"

        result1 = stats1.run()
        num1 = result1.outputs.out_stat

        mask_file = work_dir / f"choroid_{side}.nii.gz"
        sdt_file = work_dir / side / f"{struct_stem}_sdt.nii.gz"

        stats2 = fsl.ImageStats()
        stats2.inputs.index_mask_file = mask_file
        stats2.inputs.in_file = sdt_file
        stats2.inputs.op_string = "-M"

        result2 = stats2.run()
        num2 = result2.outputs.out_stat

        exposure = num1*num2
        if side == "left":
            left_exposures.append(exposure)
        else:
            right_exposures.append(exposure)
# %%
struct_names = []
index = []
for item in file_names:
    struct_stem = (item.split(".")[0])
    index.append(re.match(r"(\d+)", struct_stem)[1])
    struct_name = re.sub(r"(\d+)-([\w-]+)", r"\2_\1", struct_stem)
    struct_name = re.sub("-", "_", struct_name)
    struct_names.append(struct_name)

df = pd.DataFrame({"index": index, "struct_name": struct_names, "left_exposure": left_exposures, "right_exposure": right_exposures})
df.set_index("index", inplace=True)
df.to_csv("/home/srs-9/Projects/ms_mri/data/mni_exposures2.csv")