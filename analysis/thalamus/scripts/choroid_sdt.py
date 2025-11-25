import csv
import os
import shutil
from pathlib import Path
import subprocess
from tqdm import tqdm


data_file_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")

aschoplex_inf = Path("/media/smbshare/srs-9/aschoplex/test1/work_dir/working_directory_prediction_finetuning/ensemble_prediction")
label_Tr = Path("/media/smbshare/srs-9/aschoplex/test1/label_Tr")

save_root = Path("/media/smbshare/srs-9/thalamus_project/data")

with open(data_file_dir/"subject-sessions.csv", 'r') as f:
    reader = csv.reader(f)
    subject_sessions = [row for row in reader]

didnt_exist = []
for sub, ses in tqdm(subject_sessions, total=len(subject_sessions)):
    subject_folder = save_root / f"sub{sub}-{ses}"
    if not subject_folder.exists():
        os.makedirs(subject_folder)

    choroid_orig = aschoplex_inf / f"MRI_{sub}_image_ensemble_seg.nii.gz"
    if not choroid_orig.exists():
        choroid_orig = label_Tr / f"MRI_{sub}_seg.nii.gz"
    if not choroid_orig.exists():
        didnt_exist.append(sub)
        continue

    choroid2 = subject_folder / "choroid.nii.gz"
    if not choroid2.exists():
        shutil.copyfile(choroid_orig, choroid2)

    choroid_sdt = subject_folder / "choroid-sdt.nii.gz"
    if not choroid_sdt.exists():
        cmd = ["c3d", str(choroid2), "-sdt", "-o", str(choroid_sdt)]
        try:
            subprocess.run(cmd)
        except Exception:
            continue

with open("choroid_sdt_out.txt", 'w') as f:
    for line in didnt_exist:
        f.write(line + "\n")

