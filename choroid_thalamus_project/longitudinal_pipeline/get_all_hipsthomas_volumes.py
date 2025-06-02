# %%
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess

#! Update this to use the individual files hips thomas creates instead of how it is now 


def analyze_single_mask(index_mask, jacobian):
    cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
    m_result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        m_val = float(m_result.stdout)
    except (TypeError, ValueError):
        m_val = None

    cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
    v_result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        v_val = float(v_result.stdout.split(" ")[1])
    except (AttributeError, TypeError, IndexError, ValueError):
        v_val = None

    return m_val, v_val

def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", "r") as f:
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

            csv_savename = folder / f"hipsthomas_full_jacobianinv-{sesid}.csv"
            if csv_savename.exists():
                continue

            jacobian = work_dir / f"jacobianinv-t1_{sesid}.nii.gz"

            m_vals = []
            v_vals = []

            index_mask = folder / "1-THALAMUS.nii.gz"
            struct_inds = [1] + thomas_inds
            m_val, v_val = analyze_single_mask(index_mask, jacobian)
            m_vals.append(m_val)
            v_vals.append(v_val)

            index_mask = folder / f"thomasfull_{side}.nii.gz"

            cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
            m_result = subprocess.run(cmd, capture_output=True, text=True)

            cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
            v_result = subprocess.run(cmd, capture_output=True, text=True)

            m_lines = m_result.stdout.split("\n")
            v_lines = v_result.stdout.split("\n")

            for i in thomas_inds:
                try:
                    m_vals.append(float(m_lines[i - 1]))
                except ValueError:
                    m_vals.append(1)
                try:
                    v_vals.append(float(v_lines[i - 1].split(" ")[1]))
                except ValueError:
                    v_vals.append(0)

            index_mask = folder / "33-GP.nii.gz"
            struct_inds = struct_inds + [33]
            m_val, v_val = analyze_single_mask(index_mask, jacobian)
            m_vals.append(m_val)
            v_vals.append(v_val)

            index_mask = folder / "34-Amy.nii.gz"
            struct_inds = struct_inds + [34]
            m_val, v_val = analyze_single_mask(index_mask, jacobian)
            m_vals.append(m_val)
            v_vals.append(v_val)

            data = {"volumes": v_vals, "jac_det": m_vals}
            df = pd.DataFrame(data, index=struct_inds)
            df.index.name = "struct"
            df.to_csv(csv_savename)


if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)

# %%
