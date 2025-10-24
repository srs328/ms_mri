# ...existing code...
from pathlib import Path
import os
import subprocess
import csv
from loguru import logger
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

logger.remove()
logger.add(sys.stderr, level="INFO")
curr_file = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_file)
logger.add(os.path.join(curr_dir, "segment.log"), level="DEBUG")

dataroot = Path("/mnt/h/srs-9/thalamus_project/data")
data_file_dir = Path("/home/srs-9/Projects/ms_mri/data")
subses_file = data_file_dir / "subject-sessions.csv"
segment_csf_script = "/home/srs-9/Projects/ms_mri/analysis/thalamus/csf_segmentation/segment_csf.sh"

def run_subject(root: Path, force: bool=False, dry_run: bool=False):
    root = Path(root)
    final = root / "peripheral_CSF.nii.gz"
    subj_log = root / "segment_driver.log"

    if final.exists() and final.stat().st_size > 0 and not force:
        logger.info(f"SKIP subject {root.name}: {final.name} exists")
        return 0, f"skipped {root.name}"

    cmd = ["bash", segment_csf_script, str(root)]
    logger.info("CMD: " + " ".join(cmd))
    if dry_run:
        logger.info(f"DRY-RUN: would run {cmd}")
        return 0, "dry-run"

    with open(subj_log, "ab") as lg:
        try:
            proc = subprocess.run(cmd, check=True, capture_output=True)
            lg.write(b"=== STDOUT ===\n")
            lg.write(proc.stdout)
            lg.write(b"\n=== STDERR ===\n")
            lg.write(proc.stderr)
            logger.info(f"OK {root.name}")
            return 0, "ok"
        except subprocess.CalledProcessError as e:
            lg.write(b"\n=== ERROR ===\n")
            lg.write(e.stdout or b"")
            lg.write(e.stderr or b"")
            logger.error(f"FAILED {root.name}: returncode {e.returncode}")
            return e.returncode, e.stderr.decode('utf-8', errors='replace')

def main(args):
    with open(subses_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        subject_sessions = [(sub, ses) for sub, ses in reader]

    subjects = []
    for sub, ses in subject_sessions:
        subjects.append(dataroot / f"sub{sub}-{ses}")

    # optionally limit subjects for quick tests
    if args.limit:
        subjects = subjects[:args.limit]

    if args.jobs == 1:
        results = [run_subject(s, force=args.force, dry_run=args.dry_run) for s in subjects]
    else:
        results = []
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = {ex.submit(run_subject, s, args.force, args.dry_run): s for s in subjects}
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                logger.debug(res.stderr if res[0] != 0 else "")

    # summary
    ok = sum(1 for r in results if r[0] == 0)
    fail = len(results) - ok
    logger.info(f"Done. OK: {ok}, FAIL: {fail}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run segment_csf.sh over dataset")
    p.add_argument("--force", action="store_true", help="re-run even if outputs exist")
    p.add_argument("--dry-run", action="store_true", help="don't execute commands")
    p.add_argument("--jobs", type=int, default=1, help="number of parallel jobs (default 1)")
    p.add_argument("--limit", type=int, default=None, help="limit number of subjects (for testing)")
    args = p.parse_args()
    main(args)
# ...existing code...