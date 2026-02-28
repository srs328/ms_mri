#%% 
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path
from loguru import logger
import sys

import subprocess 


def fslstats(mask_file, stat_flags, index_mask=None):
        """
        Run fslstats and return results as a list of floats.
        
        Parameters
        ----------
        mask_file : str
            Path to the input image
        stat_flags : str or list
            Stats flags e.g. '-M' or ['-M', '-S']
        index_mask : str, optional
            Path to index mask file (for -K option)
        
        Returns
        -------
        list of float (single stat) or list of lists (multiple stats per label)
        """
        if isinstance(stat_flags, str):
            stat_flags = stat_flags.split()
        
        cmd = ['fslstats']
        if index_mask:
            cmd += ['-K', index_mask]
        cmd += [mask_file] + stat_flags
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        
        parsed = []
        for line in lines:
            values = [float(v) for v in line.split()]
            if len(values) == 1:
                parsed.append(values[0])
            elif len(values) == 0:
                parsed.append([None])
            else:
                parsed.append(values)
        if len(parsed) == 0:
            parsed = [None]
        return parsed


#%%
def main():
    now = datetime.now()
    log_filename = now.strftime(
        f"{os.path.basename(__file__).split('.')[0]}-%Y%m%d_T%H%M%S.log"
    )
    logger.remove()
    logger.add(sys.stdout, level="INFO", filter=lambda record: record["level"].no < logger.level("WARNING").no)
    # Add a sink for WARNING level and above to stderr
    # This sink will handle WARNING, ERROR, CRITICAL
    logger.add(sys.stderr, level="WARNING")
    # logger.add(log_filename, mode="w")


    subject_sessions = pd.read_csv("/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
    # subject_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")

    # # dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
    # dataroot = Path("/home/srs-9/hpc/data/longitudinal")
    # data_dir = Path("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/data0")

    subid = int(sys.argv[1])
    logger.info(f"Starting sub{subid}")
    # subid = 1001
    dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
    # dataroot = Path("/home/srs-9/hpc/data/longitudinal")

    KEY_REF = [
        "1-THALAMUS.nii.gz",
        "10-MGN.nii.gz",
        "11-CM.nii.gz",
        "12-MD-Pf.nii.gz",
        "13-Hb.nii.gz",
        "14-MTT.nii.gz",
        "2-AV.nii.gz",
        "26-Acc.nii.gz",
        "27-Cau.nii.gz",
        "28-Cla.nii.gz",
        "29-GPe.nii.gz",
        "30-GPi.nii.gz",
        "31-Put.nii.gz",
        "32-RN.nii.gz",
        "33-GP.nii.gz",
        "34-Amy.nii.gz",
        "4-VA.nii.gz",
        "4567-VL.nii.gz",
        "5-VLa.nii.gz",
        "6-VLP.nii.gz",
        "6_VLPd.nii.gz",
        "6_VLPv.nii.gz",
        "7-VPL.nii.gz",
        "8-Pul.nii.gz",
        "9-LGN.nii.gz",
        "15-CL.nii.gz",
        "thomas_anterior.nii.gz",
        "thomas_ventral.nii.gz",
        "thomas_medial.nii.gz",
        "thomas_posterior.nii.gz",
    ]

    


    # %%

    ses1 = subject_sessions.loc[subid, 'ses1']
    ses2 = subject_sessions.loc[subid, 'ses2']
    group_dir = dataroot / f"sub{subid}/group"

    if not (group_dir / "bilateral" / "15-CL.nii.gz").exists():
        logger.info("Running combineNuclei.sh")
        subprocess.run(["bash", "/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/two_point/combineNuclei.sh", group_dir])

    ses1_jac = str(group_dir / f"sub{subid}_input0000-t1_brain_wmn_{ses1}-1Warp-Jacobian00.nii.gz")
    ses2_jac = str(group_dir / f"sub{subid}_input0001-t1_brain_wmn_{ses2}-1Warp-Jacobian00.nii.gz")

    thomas_left_dir = group_dir / "left"
    thoams_right_dir = group_dir / "right"
    thoams_full_dir = group_dir / "bilateral"

    left_defs = []
    right_defs = []
    full_defs = []
    logger.info("Starting loop")
    for mask_file in tqdm(KEY_REF, total=len(KEY_REF)):
        left_mask_path = str(thomas_left_dir / mask_file)
        right_mask_path = str(thoams_right_dir / mask_file)
        full_mask_path = str(thoams_full_dir / mask_file)

        try:
            def1_left = fslstats(ses1_jac, "-M", index_mask=left_mask_path)[0]
            def2_left = fslstats(ses2_jac, "-M", index_mask=left_mask_path)[0]
        except subprocess.CalledProcessError as e:
            logger.error(f"Error on left {mask_file}")
            logger.error(e.stderr)
            raise e
            def1_left = None
            def2_left = None
        left_defs.append((mask_file.removesuffix(".nii.gz"), def1_left, def2_left))

        try:
            def1_right = fslstats(ses1_jac, "-M", index_mask=right_mask_path)[0]
            def2_right = fslstats(ses2_jac, "-M", index_mask=right_mask_path)[0]
        except subprocess.CalledProcessError as e:
            logger.error(f"Error on right {mask_file}")
            logger.error(e.stderr)
            raise
            print(e.stderr)
            def1_right = None
            def2_right = None
        right_defs.append((mask_file.removesuffix(".nii.gz"), def1_right, def2_right))

        try:
            def1_full = fslstats(ses1_jac, "-M", index_mask=full_mask_path)[0]
            def2_full = fslstats(ses2_jac, "-M", index_mask=full_mask_path)[0]
        except subprocess.CalledProcessError as e:
            logger.error(f"Error on bilateral {mask_file}")
            logger.error(e.stderr)
            raise e
            print(e.stderr)
            def1_full = None
            def2_full = None
        full_defs.append((mask_file.removesuffix(".nii.gz"), def1_full, def2_full))

    # %%
    df_full = pd.DataFrame(full_defs, columns=["struct", "ses1", "ses2"])
    df_right = pd.DataFrame(right_defs, columns=["struct", "ses1", "ses2"])
    df_left = pd.DataFrame(left_defs, columns=["struct", "ses1", "ses2"])

    df_full.to_csv(group_dir / f"sub{subid}_thomas_bilateral_deformations.csv", index=False)
    df_right.to_csv(group_dir / f"sub{subid}_thomas_right_deformations.csv", index=False)
    df_left.to_csv(group_dir / f"sub{subid}_thomas_left_deformations.csv", index=False)

    logger.info("Done")


if __name__ == "__main__":
    print("main")
    main()