import sys
from pathlib import Path
import json
import subprocess

def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", 'r') as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])

    for sesid in sessions:
        jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
        for side in ["L", "R"]:
            if side == "L":
                folder = work_dir / "left"
            else:
                folder = work_dir / "right"
            
            label_mask = folder / f"thomasfull_{side}.nii.gz"
            jacobian_mask = folder / f"thomasfull_{side}-jac{sesid}.nii.gz"
            cmd = ["fslmaths",
                jacobian,
                "-mas",
                label_mask,
                jacobian_mask]
            print(" ".join([str(elem) for elem in cmd]))
            subprocess.run(cmd)


if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)