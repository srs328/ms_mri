# %%
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess


def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", "r") as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    for sesid in sessions:
        for side in ["L", "R"]:
            if side == "L":
                folder = work_dir / "left"
            else:
                folder = work_dir / "right"

            csv_orig = folder / f"hipsthomas_vols_jacobians-{sesid}_fwd.csv"
            csv_savename = folder / f"hipsthomas_vols_jacobians-{sesid}_updated.csv"
            if csv_savename.exists():
                continue

            data = pd.read_csv(csv_orig, index_col="struct")
            jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
            index_mask = folder / "1-THALAMUS.nii.gz"
            cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
            m_result = subprocess.run(cmd, capture_output=True, text=True)

            cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
            print(" ".join([str(elem) for elem in cmd]))
            v_result = subprocess.run(cmd, capture_output=True, text=True)

            m_val = float(m_result.stdout)
            v_val = float(v_result.stdout.split(" ")[1])
            print(m_val, v_val)
            data.loc[1, "jac_det"] = m_val
            data.loc[1, "volumes"] = v_val

            print(csv_savename)
            data.to_csv(csv_savename)


if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)
