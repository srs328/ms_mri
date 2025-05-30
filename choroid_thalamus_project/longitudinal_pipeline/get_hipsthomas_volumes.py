# %%
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess

def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", 'r') as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    thomas_inds = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 26, 27, 28, 29, 30, 31, 32]

    for sesid in sessions:
        for side in ["L", "R"]:
            if side == "L":
                folder = work_dir / "left"
            else:
                folder = work_dir / "right"

            csv_savename = folder / f"hipsthomas_vols_jacobians-{sesid}_fwd.csv"
            if csv_savename.exists():
                continue

            jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"
            index_mask = folder / f"thomasfull_{side}.nii.gz"

            cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
            m_result = subprocess.run(cmd, capture_output=True, text=True)

            cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
            print(" ".join([str(elem) for elem in cmd]))
            v_result = subprocess.run(cmd, capture_output=True, text=True)

            m_lines = m_result.stdout.split("\n")
            v_lines = v_result.stdout.split("\n")
            m_vals = []
            v_vals = []

            for i in thomas_inds:
                m_vals.append(float(m_lines[i-1]))
                v_vals.append(float(v_lines[i-1].split(" ")[1]))

            data = {'volumes': v_vals, 'jac_det': m_vals}
            df = pd.DataFrame(data, index=thomas_inds)
            df.index.name = "struct"
            df.to_csv(folder / f"hipsthomas_vols_jacobians-{sesid}_fwd.csv")


if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)

# %%
