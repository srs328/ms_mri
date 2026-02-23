#!/usr/bin/env python3
"""
Extract ifod2act NeMo outputs from batched zip files into per-subject chaco1 folders.
Strips the scanID- prefix from subject-specific files.
Skips files that already exist. Also copies the batch config (json) and log (txt)
into each subject's chaco1 folder (names unchanged).
"""

import re
import zipfile
import logging
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
chacoroot   = Path("/mnt/h/srs-9/chaco")
batched_dir = chacoroot / "chaco1_batched_results"

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(chacoroot / "extract_chaco_results.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Regex to extract scan ID from filename ─────────────────────────────────────
SCAN_ID_RE = re.compile(r'^(sub\d{4}-\d{8})-')


def get_scan_id_and_stripped_name(filename):
    """
    Returns (scan_id, stripped_filename) if filename starts with scanID-,
    otherwise returns (None, None).
    """
    m = SCAN_ID_RE.match(filename)
    if not m:
        return None, None
    scan_id = m.group(1)
    stripped = filename[len(scan_id) + 1:]  # remove "subXXXX-YYYYMMDD-"
    return scan_id, stripped


def extract_file(zf, name, out_path):
    """Write a single file from zip to out_path."""
    with zf.open(name) as src, open(out_path, 'wb') as dst:
        dst.write(src.read())


def extract_zip(zip_path):
    log.info(f"Processing {zip_path.name}")
    skipped = 0
    copied  = 0

    with zipfile.ZipFile(zip_path, 'r') as zf:
        all_names = zf.namelist()

        # Batch-level files (same copy goes into every subject's folder)
        config_names = [n for n in all_names if n.endswith('.json')]
        log_names    = [n for n in all_names if n.endswith('_log.txt')]

        # Subject-specific ifod2act files
        ifod2act_names = [
            n for n in all_names
            if 'ifod2act' in n and not n.endswith('/') and not n.endswith(".txt") and not n.endswith(".json")
        ]

        # Collect unique scan IDs and build the copy plan
        # plan: list of (zip_name, out_dir, out_filename)
        plan = []
        scan_ids = set()

        for name in ifod2act_names:
            fname = Path(name).name
            scan_id, stripped = get_scan_id_and_stripped_name(fname)
            if not scan_id:
                log.warning(f"  Could not extract scan ID from: {fname} — skipping")
                continue
            scan_ids.add(scan_id)
            out_dir = chacoroot / scan_id / "chaco1"
            plan.append((name, out_dir, stripped))

        if not scan_ids:
            log.warning(f"  No recognisable scan IDs found in {zip_path.name}")
            return

        # Execute the copy plan for ifod2act files
        for zip_name, out_dir, out_fname in plan:
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / out_fname
            if out_path.exists():
                skipped += 1
                continue
            extract_file(zf, zip_name, out_path)
            copied += 1

        # Copy batch config and log into every subject's chaco1 folder unchanged
        for scan_id in scan_ids:
            out_dir = chacoroot / scan_id / "chaco1"
            out_dir.mkdir(parents=True, exist_ok=True)
            for name in config_names + log_names:
                out_path = out_dir / Path(name).name
                if out_path.exists():
                    skipped += 1
                    continue
                extract_file(zf, name, out_path)
                copied += 1

    log.info(f"  Done — {copied} files copied, {skipped} already existed and skipped")


def main():
    zip_files = sorted(batched_dir.glob("*.zip"))
    if not zip_files:
        log.warning(f"No zip files found in {batched_dir}")
        return

    log.info(f"Found {len(zip_files)} zip file(s) to process")
    for zip_path in zip_files:
        try:
            extract_zip(zip_path)
        except Exception as e:
            log.error(f"Failed to process {zip_path.name}: {e}")

    log.info("All done.")


if __name__ == "__main__":
    main()