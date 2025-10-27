#%%
from pathlib import Path
import nibabel as nib
import subprocess
import os
import re
from nipype.interfaces import fsl
from tqdm.notebook import tqdm
import pandas as pd
import numpy as np

#%%

#! Pre steps that I did in terminal:
#   Created left and right hemisphere mask with instructions (https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=fsl;e4c252f3.1406) to split choroid into left and right

# work_dir = Path("/media/smbshare/srs-9/hipsthomas/MNI152_T1_1mm")
work_dir = Path("/mnt/h/srs-9/hips-thomas/MNI152_T1_1mm")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")


file_items = [item.name for item in os.scandir(work_dir/"left") if item.is_file()]
file_names = []
for item in file_items:
    if re.match(r"\d{1,2}-.+(?<!_sdt)\.nii\.gz", item):
        file_names.append(item)

# Added this 10/26/25, much later than this file was created
file_names = ["2-AV.nii.gz", "4-VA.nii.gz", "5-VLa.nii.gz", "6-VLP.nii.gz", "7-VPL.nii.gz",
              "8-Pul.nii.gz", "9-LGN.nii.gz", "10-MGN.nii.gz", "11-CM.nii.gz", "12-MD-Pf.nii.gz",
              "13-Hb.nii.gz", "14-MTT.nii.gz", "26-Acc.nii.gz", "27-Cau.nii.gz", "28-Cla.nii.gz", 
              "29-GPe.nii.gz", "30-GPi.nii.gz", "31-Put.nii.gz", "32-RN.nii.gz"]
#%%

for name in file_names:
    filepath = work_dir / "left" / name
    filestem = filepath.stem.split(".")[0]

    out = work_dir / "left" / f"{filestem}_sdt.nii.gz"
    if not out.exists():
        cmd = ["c3d", filepath, "-sdt", "-o", out]
        subprocess.run(cmd)

    filepath = work_dir / "right" / name
    out = work_dir / "right" / f"{filestem}_sdt.nii.gz"
    if not out.exists():
        cmd = ["c3d", filepath, "-sdt", "-o", out]
        subprocess.run(cmd)

#%%

sdt_file = work_dir / "ventricle_left_sdt.nii.gz"
sdt = nib.load(sdt_file).get_fdata()

for file in file_names:
    mask_file = work_dir / "left" / file
    mask = nib.load(mask_file).get_fdata()

    struct_points = np.where(mask > 0)

    dists = []
    for i in range(struct_points[0].shape[0]):
        dists.append(sdt[struct_points[0][i], struct_points[1][i], struct_points[2][i]])
    
    print("\n"+file)
    print(np.min(dists), np.max(dists), np.mean(dists))
#%%

left_exposures = []
right_exposures = []
for item in tqdm(file_names, total=len(file_names)):
    struct_stem = item.split(".")[0]
    for side in ["left", "right"]:
        mask_file = work_dir / side / f"{struct_stem}.nii.gz"
        sdt_file = work_dir / f"choroid_{side}_sdt.nii.gz"
        
        # Added this 10/26/25, much later than this file was created
        sdt_file = work_dir / "outer_CSF_SDT.nii.gz"

        stats1 = fsl.ImageStats()
        stats1.inputs.index_mask_file = mask_file
        stats1.inputs.in_file = sdt_file
        stats1.inputs.op_string = "-M"

        result1 = stats1.run()
        num1 = result1.outputs.out_stat

        # mask_file = work_dir / f"choroid_{side}.nii.gz"
        # sdt_file = work_dir / side / f"{struct_stem}_sdt.nii.gz"

        # stats2 = fsl.ImageStats()
        # stats2.inputs.index_mask_file = mask_file
        # stats2.inputs.in_file = sdt_file
        # stats2.inputs.op_string = "-M"

        # result2 = stats2.run()
        # num2 = result2.outputs.out_stat

        # exposure = num1*num2
        exposure = num1
        # exposure = (num1+num2)/2
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
df.to_csv("/home/srs-9/Projects/ms_mri/data/mni_outer_CSF_SDT.csv")