import sys
from pathlib import Path
import json
import subprocess


def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"
    with open(dataroot / "subject-sessions-longit.json", 'r') as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    script_path = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/computeJacobian.sh"
    for i, sesid in enumerate(sessions):
        forward_warp = work_dir / f"sub{subid}_input000{i}-t1_{sesid}_mniWarped-1Warp.nii.gz"
        inv_warp = work_dir / f"sub{subid}_input000{i}-t1_{sesid}_mniWarped-1InverseWarp.nii.gz"
        jacobian = work_dir / f"jacobian-t1_{sesid}.nii.gz"
        jacobian_inv = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
        
        if not jacobian.exists():
            # cmd = ["bash", "CreateJacobianDeterminantImage", "3", forward_warp, jacobian]
            cmd = ["bash", script_path, forward_warp, jacobian]
            print(" ".join([str(part) for part in cmd]))
            subprocess.run(cmd)

        if not jacobian_inv.exists():
            # cmd = ["bash", "CreateJacobianDeterminantImage", "3", inv_warp, jacobian_inv]
            cmd = ["bash", script_path, inv_warp, jacobian_inv]
            print(" ".join([str(part) for part in cmd]))
            subprocess.run(cmd)

if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)