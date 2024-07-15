import os
from pathlib import Path
import importlib
import numpy as np
import nibabel as nib
import data_file_manager as datafm


def load_scan(scan_path: Path) -> np.ndarray:
    img = nib.load(scan_path)
    return np.array(img.dataobj)


# def stack_scans(subject, modalities):
#     scan_paths = [lesjak_datafm.get_scan(subject, mod) for mod in modalities]


def main():
    basepath = Path("/mnt/f/Data/ms_mri/lesjak_2017")
    data_dir = basepath / "data"
    lesjak_datafm = datafm.LesjakData(data_dir)
    subjects = lesjak_datafm.subjects
    modalities = ["FLAIR", "T1W", "T1WKS", "T2W"]

    for subject in subjects:
        scan_paths = [lesjak_datafm.get_scan(subject, mod) for mod in modalities]
        scans = [load_scan(path) for path in scan_paths]
        scan_struct = np.stack(scans, axis=-1)
        


if __name__ == "__main__":
    basepath = Path("/mnt/f/Data/ms_mri/lesjak_2017")
    data_dir = basepath / "data"
    lesjak_datafm = datafm.LesjakData(data_dir)
    subjects = lesjak_datafm.subjects
    modalities = ["FLAIR", "T1W", "T1WKS", "T2W"]
