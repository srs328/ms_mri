from pathlib import Path
import shutil
import os
from loguru import logger

from mri_data.file_manager import DataSet, scan_3Tpioneer_bids
from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

logger.remove()

drive_root = fm.get_drive_root()
msmri_home = Path("/home/srs-9/Projects/ms_mri")
training_work_dirs = drive_root / "training_work_dirs"
dataroot = drive_root / "3Tpioneer_bids"
clinical_data_root = drive_root / "Secure_Data" / "Large"
project_dataroot = msmri_home / "data"


work_dir_names = [
    "choroid_pineal_pituitary3",
    "choroid_pineal_pituitary3-2",
    "choroid_pineal_pituitary3-3",
    "choroid_pineal_pituitary3-4",
]
work_dirs = [training_work_dirs / name / "ensemble_output" for name in work_dir_names]
ensemble_datasets = [
    fm.scan_3Tpioneer_bids(work_dir, label="flair.t1_ensemble.nii.gz")
    for work_dir in work_dirs
]

copy_root = drive_root / "analysis" / "choroid_pineal_pituitary-crosstrain"


subjects = []
for dataset in ensemble_datasets:
    for scan in dataset:
        subjects.append(int(scan.subid))


def has_subject(scan, subjects: list[int]) -> bool:
    if int(scan.subid) in subjects:
        return True
    else:
        return False


orig_dataset_proc = DataSetProcesser.new_dataset(
    dataroot, fm.scan_3Tpioneer_bids, filters=fm.filter_first_ses
)
orig_dataset_proc.filter([has_subject], [(subjects,)])
orig_dataset_proc.prepare_labels(
    ["choroid_t1_flair", "pineal", "pituitary"], ["CH", "SRS", "DT", "ED"]
)
orig_dataset = orig_dataset_proc.dataset


for scan in orig_dataset:
    new_dir = copy_root / scan.relative_path
    os.makedirs(new_dir, exist_ok=True)

    if not (new_dir / scan.label_path.name).is_file():
        shutil.copyfile(scan.label_path, new_dir / scan.label_path.name)

    flair = scan.root / "flair.nii.gz"
    flair_symlink = new_dir / "flair.nii.gz"
    if not flair_symlink.exists():
        os.symlink(flair, flair_symlink)

    t1 = scan.root / "t1.nii.gz"
    t1_symlink = new_dir / "t1.nii.gz"
    if not t1_symlink.exists():
        os.symlink(t1, t1_symlink)


for dataset in ensemble_datasets:
    for scan in dataset:
        new_dir = copy_root / scan.relative_path
        if not (new_dir / scan.label_path.name).is_file():
            shutil.copyfile(scan.label_path, new_dir / scan.label_path.name)
