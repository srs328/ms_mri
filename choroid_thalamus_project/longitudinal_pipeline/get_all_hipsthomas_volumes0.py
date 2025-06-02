# %%
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess
import re

#! Update this to use the individual files hips thomas creates instead of how it is now 


def main(subid, dataroot, work_home):
    work_dir = work_home / f"sub{subid}"

    with open(dataroot / "subject-sessions-longit.json", "r") as f:
        subjects = json.load(f)
    sessions = sorted(subjects[subid])
    # just copy first and last to speed things up
    sessions = sorted(sessions)
    sessions = [sessions[0], sessions[-1]]

    with open("/home/srs-9/Projects/ms_mri/choroid_thalamus_project/longitudinal_pipeline/structs.txt", 'r') as f:
        struct_filenames = [line.strip() for line in f.readlines()]
    
    structures = []
    for name in struct_filenames:
        ind = int(re.search(r"^(\d+).+.nii.gz", name)[1])
        structures.append((ind, name))

    structures.sort(key=lambda s: s[0])
    thomas_inds = [item[0] for item in structures]
    full_names = []
    for _, struct in structures:
        full_names.append(re.search(r"(.+).nii.gz", struct)[1])

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
            for _, struct in structures:
                index_mask = folder / struct

                cmd = ["fslstats", "-K", index_mask, jacobian, "-M"]
                print(" ".join([str(item) for item in cmd]))
                m_result = subprocess.run(cmd, capture_output=True, text=True)
                try:
                    m_val = float(m_result.stdout)
                except TypeError:
                    m_val = None
                m_vals.append(m_val)

                cmd = ["fslstats", "-K", index_mask, jacobian, "-V"]
                print(" ".join([str(item) for item in cmd]))
                v_result = subprocess.run(cmd, capture_output=True, text=True)
                try:
                    v_val = float(v_result.stdout.split(" ")[1])
                except (AttributeError, TypeError, IndexError):
                    v_val = None
                v_vals.append(v_val)

            
            data = {"fullname": full_names, "volumes": v_vals, "jac_det": m_vals}
            df = pd.DataFrame(data, index=thomas_inds)
            df.index.name = "struct"
            df.to_csv(csv_savename)


if __name__ == "__main__":
    subid = sys.argv[1]
    dataroot = Path(sys.argv[2])
    work_home = Path(sys.argv[3])
    main(subid, dataroot, work_home)

# %%
