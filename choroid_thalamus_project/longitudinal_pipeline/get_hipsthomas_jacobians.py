import sys
from pathlib import Path
import json
import subprocess

subid = sys.argv[1]
dataroot = Path(sys.argv[2])
work_home = Path(sys.argv[3])
work_dir = work_home / f"sub{subid}"

with open(dataroot / "subject-sessions-longit.json", 'r') as f:
    subjects = json.load(f)
sessions = sorted(subjects[subid])


thomas_inds = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 26, 27, 28, 29, 30, 31, 32, 33, 34]
for ind in thomas_inds:
    ind = str(ind)
    left_mask = work_dir / "left" / f"label{ind}.nii.gz"
    cmdL = ["fslmaths", 
            str(work_dir / "left" / "thomasfull_L.nii.gz"),
            "-thr",
            ind,
            "-uthr",
            ind,
            str(left_mask)]
    print(" ".join(cmdL))
    subprocess.run(cmdL)

    right_mask = work_dir / "right" / f"label{ind}.nii.gz"
    cmdR = ["fslmaths", 
            str(work_dir / "right" / "thomasfull_R.nii.gz"),
            "-thr",
            ind,
            "-uthr",
            ind,
            str(right_mask)]
    print(" ".join(cmdR))
    subprocess.run(cmdR)

    for i, sesid in enumerate(sessions):
        jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
        
        left_masked_jacobian = ".".join(str(left_mask).split(".")[:-2]) +  f"-jacobianinv-{sesid}.nii.gz"
        mask_left_cmd = ["fslmaths",
                         str(jacobian),
                         "-mas",
                         str(left_mask),
                         str(left_masked_jacobian)]
        print(" ".join(mask_left_cmd))
        subprocess.run(mask_left_cmd)

        right_masked_jacobian = ".".join(str(right_mask).split(".")[:-2]) +  f"-jacobianinv-{sesid}.nii.gz"
        mask_right_cmd = ["fslmaths",
                         str(jacobian),
                         "-mas",
                         str(right_mask),
                         str(right_masked_jacobian)]
        print(" ".join(mask_right_cmd))
        subprocess.run(mask_right_cmd)

