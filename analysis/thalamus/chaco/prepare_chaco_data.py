#!/usr/bin/env python3
"""
Pipeline to register T1, HIPS-THOMAS segmentation, and lesion masks to MNI space
for all subjects, in preparation for NeMo/ChaCo analysis.
"""

import subprocess
import logging
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
work_dir = Path("/mnt/h/srs-9/chaco")
mni      = Path("/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii.gz")
csv_path = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv")

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(work_dir / "pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────
def run(cmd, cwd=None):
    """Run a shell command, raising an exception on failure."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result


def ensure_thomasfull(scan_dir, scan_id):
    """
    Return path to thomasfull.nii.gz, creating it from L/R halves if needed.
    Raises RuntimeError if creation fails.
    """
    thomas = scan_dir / "thomasfull.nii.gz"
    if thomas.exists():
        return thomas

    log.info(f"[{scan_id}] thomasfull.nii.gz not found — attempting to create from L/R halves")
    cmd = (
        f"fslmaths {scan_dir}/thomasfull_L.nii.gz "
        f"-add {scan_dir}/thomasfull_R.nii.gz "
        f"{thomas}"
    )
    run(cmd)   # caller catches RuntimeError
    return thomas


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    work_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    skipped = []

    for i, row in df.iterrows():
        if i>1:
            return
        sub = str(row["sub"]).zfill(4)
        ses = str(row["ses"])
        scan_id  = f"sub{sub}-{ses}"
        scan_dir = dataroot / scan_id
        out_dir  = work_dir / scan_id
        out_dir.mkdir(parents=True, exist_ok=True)

        log.info(f"[{scan_id}] Starting")

        # ── 1. Check lst-ai exists ─────────────────────────────────────────────
        lst_src = scan_dir / "lst-ai" / "space-flair_desc-annotated_seg-lst.nii.gz"
        if not (scan_dir / "lst-ai").exists():
            msg = f"[{scan_id}] lst-ai folder not found — skipping"
            log.warning(msg)
            skipped.append((scan_id, "lst-ai folder missing"))
            continue

        # ── 2. Ensure thomasfull.nii.gz exists ────────────────────────────────
        try:
            thomas_src = ensure_thomasfull(scan_dir, scan_id)
        except RuntimeError as e:
            msg = f"[{scan_id}] Failed to create thomasfull.nii.gz: {e}"
            log.warning(msg)
            skipped.append((scan_id, "thomasfull creation failed"))
            continue

        # ── 3. ANTs registration: T1 → MNI ────────────────────────────────────
        t1 = scan_dir / "t1.nii.gz"
        warp   = out_dir / "t1_mni1Warp.nii.gz"
        affine = out_dir / "t1_mni0GenericAffine.mat"

        if warp.exists() and affine.exists():
            log.info(f"[{scan_id}] Registration outputs already exist — skipping registration")
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
                skipped.append((scan_id, "ANTs registration failed"))
                continue

        # ── 4. Apply transforms ────────────────────────────────────────────────
        transforms = f"-t {warp} -t {affine}"

        # 4a. HIPS-THOMAS segmentation
        thomas_mni = out_dir / "thomasfull_mni.nii.gz"
        log.info(f"[{scan_id}] Applying transforms to thomasfull")
        try:
            run(
                f"antsApplyTransforms -d 3 "
                f"-i {thomas_src} -r {mni} -o {thomas_mni} "
                f"{transforms} -n NearestNeighbor"
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] antsApplyTransforms (thomas) failed: {e}")
            skipped.append((scan_id, "antsApplyTransforms thomas failed"))
            continue

        # 4b. Lesion mask
        lst_mni = out_dir / "space-flair_desc-annotated_seg-lst_mni.nii.gz"
        log.info(f"[{scan_id}] Applying transforms to lesion mask")
        try:
            run(
                f"antsApplyTransforms -d 3 "
                f"-i {lst_src} -r {mni} -o {lst_mni} "
                f"{transforms} -n NearestNeighbor"
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] antsApplyTransforms (lesion) failed: {e}")
            skipped.append((scan_id, "antsApplyTransforms lesion failed"))
            continue

        # ── 5. Post-processing ─────────────────────────────────────────────────
        thomas_out = out_dir / "thomas_thalamus.nii.gz"
        lesion_out = out_dir / "lesion_mask_mni.nii.gz"

        # thomasfull_mni → thomas_thalamus
        log.info(f"[{scan_id}] Post-processing thomasfull_mni")
        try:
            run(
                f"fslmaths {thomas_mni} -uthr 12 -thr 4 -sub 2 -thr 0 {thomas_out}"
            )
            run(
                f"fslmaths {thomas_mni} -uthr 2 -sub 1 -thr 0 -add {thomas_out} {thomas_out}"
            )
        except RuntimeError as e:
            log.warning(f"[{scan_id}] fslmaths (thomas) failed: {e}")
            skipped.append((scan_id, "fslmaths thomas failed"))
            continue

        # lesion_mni → binarised lesion mask
        log.info(f"[{scan_id}] Binarising lesion mask")
        try:
            run(f"fslmaths {lst_mni} -bin {lesion_out}")
        except RuntimeError as e:
            log.warning(f"[{scan_id}] fslmaths (lesion bin) failed: {e}")
            skipped.append((scan_id, "fslmaths lesion binarise failed"))
            continue

        log.info(f"[{scan_id}] Done")

    # ── Summary ────────────────────────────────────────────────────────────────
    log.info("=" * 60)
    if skipped:
        log.info(f"Skipped {len(skipped)} scan(s):")
        for scan_id, reason in skipped:
            log.info(f"  {scan_id}: {reason}")
    else:
        log.info("All scans completed successfully.")


if __name__ == "__main__":
    main()