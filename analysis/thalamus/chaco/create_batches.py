#!/usr/bin/env python3
"""
Creates zip files containing batches of up to 10 lesion masks for NeMo web interface submission.
Only includes MS patients. Masks are renamed to scanID-lesion_mask_mni.nii.gz within each zip.
"""

import zipfile
import pandas as pd
from pathlib import Path

BATCH_SIZE = 10

work_dir = Path("/mnt/h/srs-9/chaco")
zip_dir = Path("/mnt/h/chaco_batches")

def main():
    subject_data = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv",
        index_col="subid"
    )
    ms_subs = set(subject_data.index[subject_data["dz_type2"] == "MS"])

    all_masks = sorted(work_dir.glob("sub*-*/lesion_mask_mni.nii.gz"))
    lesion_masks = [
        p for p in all_masks
        if int(p.parent.name.split("sub")[1].split("-")[0]) in ms_subs
    ]

    print(f"Found {len(all_masks)} total masks, {len(lesion_masks)} from MS subjects")

    if not lesion_masks:
        print("No MS lesion masks found.")
        return

    batches = [lesion_masks[i:i + BATCH_SIZE] for i in range(0, len(lesion_masks), BATCH_SIZE)]

    for batch_num, batch in enumerate(batches, start=1):
        zip_path = zip_dir / f"lesion_batch_{batch_num:03d}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for mask_path in batch:
                scan_id = mask_path.parent.name
                arcname = f"{scan_id}-lesion_mask_mni.nii.gz"
                zf.write(mask_path, arcname=arcname)
        print(f"Created {zip_path.name} ({len(batch)} masks)")

    print(f"Done. {len(batches)} zip files created in {work_dir}")

if __name__ == "__main__":
    main()
    