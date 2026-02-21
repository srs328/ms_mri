#!/usr/bin/env python3
"""
Parallelized pipeline to register T1, HIPS-THOMAS segmentation, and lesion masks
to MNI space for all subjects, in preparation for NeMo/ChaCo analysis.
"""

import os
import subprocess
import logging
import pandas as pd
from pathlib import Path
from multiprocessing import Pool, Manager

# ── Config ─────────────────────────────────────────────────────────────────────
NUM_WORKERS = 6           # number of parallel subjects to process
ANTS_THREADS = 3          # ITK threads per ANTs job (NUM_WORKERS * ANTS_THREADS ~ total cores)
MIN_FILE_KB = 20

# ── Paths ──────────────────────────────────────────────────────────────────────
dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
work_dir = Path("/mnt/h/srs-9/chaco")
mni      = Path("/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii.gz")
csv_path = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv")

# ── Logging ────────────────────────────────────────────────────────────────────
# File handler only here — worker processes will also attach this handler.
# StreamHandler is added in main() only, to avoid duplicated console output.
log_path = work_dir / "pipeline.log"

def get_logger():
    logger = logging.getLogger("chaco_pipeline")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
    return logger


# ── Helpers ────────────────────────────────────────────────────────────────────
def run(cmd, cwd=None):
    """Run a shell command, raising RuntimeError on failure."""
    env = os.environ.copy()
    env["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = str(ANTS_THREADS)
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result


def ensure_thomasfull(scan_dir):
    thomas = scan_dir / "thomasfull.nii.gz"
    if thomas.exists() and thomas.stat().st_size > MIN_FILE_KB * 1024:
        return thomas
    run(
        f"fslmaths {scan_dir}/thomasfull_L.nii.gz "
        f"-add {scan_dir}/thomasfull_R.nii.gz "
        f"{thomas}"
    )
    return thomas



def is_valid_file(path, min_kb=MIN_FILE_KB):
    """Returns True if file exists and is larger than the minimum size threshold."""
    p = Path(path)
    return p.exists() and p.stat().st_size > min_kb * 1024


# ── Per-subject worker ─────────────────────────────────────────────────────────
def process_scan(args):
    """
    Processes a single scan. Designed to be called by a multiprocessing worker.
    Returns (scan_id, skipped_reason_or_None).
    """
    sub, ses = args
    scan_id  = f"sub{str(sub).zfill(4)}-{ses}"
    scan_dir = dataroot / scan_id
    out_dir  = work_dir / scan_id
    out_dir.mkdir(parents=True, exist_ok=True)

    log = get_logger()
    log.info(f"[{scan_id}] Starting")

    # 1. Check lst-ai
    lst_src = scan_dir / "lst-ai" / "space-flair_desc-annotated_seg-lst.nii.gz"
    if not (scan_dir / "lst-ai").exists():
        log.warning(f"[{scan_id}] lst-ai folder not found — skipping")
        return (scan_id, "lst-ai folder missing")

    # 2. Ensure thomasfull
    try:
        thomas_src = ensure_thomasfull(scan_dir)
    except RuntimeError as e:
        log.warning(f"[{scan_id}] Failed to create thomasfull.nii.gz: {e}")
        return (scan_id, "thomasfull creation failed")

    # 3. ANTs registration
    warp   = out_dir / "t1_mni1Warp.nii.gz"
    affine = out_dir / "t1_mni0GenericAffine.mat"
    t1     = scan_dir / "t1.nii.gz"

    if is_valid_file(warp) and is_valid_file(affine, min_kb=0.1):
        log.info(f"[{scan_id}] Registration already exists — skipping")
    else:
        log.info(f"[{scan_id}] Running antsRegistrationSyNQuick")
        try:
            run(
                f"antsRegistrationSyNQuick.sh -d 3 -t s "
                f"-f {mni} -m {t1} -o t1_mni",
                cwd=out_dir
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] ANTs registration failed: {e}")
            return (scan_id, "ANTs registration failed")

    # 4. Apply transforms
    transforms  = f"-t {warp} -t {affine}"
    thomas_mni  = out_dir / "thomasfull_mni.nii.gz"
    lst_mni     = out_dir / "space-flair_desc-annotated_seg-lst_mni.nii.gz"

    if not is_valid_file(thomas_mni):
        log.info(f"[{scan_id}] Applying transforms to thomasfull")
        try:
            run(
                f"antsApplyTransforms -d 3 "
                f"-i {thomas_src} -r {mni} -o {thomas_mni} "
                f"{transforms} -n NearestNeighbor"
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] antsApplyTransforms (thomas) failed: {e}")
            return (scan_id, "antsApplyTransforms thomas failed")

    if not is_valid_file(lst_mni):
        log.info(f"[{scan_id}] Applying transforms to lesion mask")
        try:
            run(
                f"antsApplyTransforms -d 3 "
                f"-i {lst_src} -r {mni} -o {lst_mni} "
                f"{transforms} -n NearestNeighbor"
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] antsApplyTransforms (lesion) failed: {e}")
            return (scan_id, "antsApplyTransforms lesion failed")

    # 5. Post-processing
    thomas_out = out_dir / "thomas_thalamus.nii.gz"
    lesion_out = out_dir / "lesion_mask_mni.nii.gz"

    if not is_valid_file(thomas_out):
        log.info(f"[{scan_id}] Post-processing thomasfull_mni")
        try:
            run(f"fslmaths {thomas_mni} -uthr 12 -thr 4 -sub 2 -thr 0 {thomas_out}")
            run(f"fslmaths {thomas_mni} -uthr 2 -sub 1 -thr 0 -add {thomas_out} {thomas_out}")
        except RuntimeError as e:
            log.warning(f"[{scan_id}] fslmaths (thomas) failed: {e}")
            return (scan_id, "fslmaths thomas failed")

    if not is_valid_file(lesion_out):
        log.info(f"[{scan_id}] Binarising lesion mask")
        try:
            run(f"fslmaths {lst_mni} -bin {lesion_out}")
        except RuntimeError as e:
            log.warning(f"[{scan_id}] fslmaths (lesion bin) failed: {e}")
            return (scan_id, "fslmaths lesion binarise failed")

    log.info(f"[{scan_id}] Done")
    return (scan_id, None)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    work_dir.mkdir(parents=True, exist_ok=True)

    # Console handler only in main process
    log = get_logger()
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    log.addHandler(ch)

    df   = pd.read_csv(csv_path)
    jobs = [(str(row["sub"]), str(row["ses"])) for _, row in df.iterrows()]

    log.info(f"Starting pipeline: {len(jobs)} scans, {NUM_WORKERS} workers, "
             f"{ANTS_THREADS} ANTs threads each")

    with Pool(processes=NUM_WORKERS) as pool:
        results = pool.map(process_scan, jobs)

    skipped = [(scan_id, reason) for scan_id, reason in results if reason is not None]

    log.info("=" * 60)
    log.info(f"Finished. {len(jobs) - len(skipped)}/{len(jobs)} scans completed successfully.")
    if skipped:
        log.info(f"Skipped {len(skipped)} scan(s):")
        for scan_id, reason in skipped:
            log.info(f"  {scan_id}: {reason}")


if __name__ == "__main__":
    main()