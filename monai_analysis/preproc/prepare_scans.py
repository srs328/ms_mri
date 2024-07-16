from __future__ import annotations
import os
from pathlib import Path
import importlib
import numpy as np
import nibabel as nib
from monai_analysis.preproc import data_file_manager as datafm
from monai_analysis.preproc.hemond_data import DataSet
import tqdm
import random


def load_scan(scan_path: Path) -> np.ndarray:
    img = nib.load(scan_path)
    return np.array(img.dataobj)


# def stack_scans(subject, modalities):
#     scan_paths = [lesjak_datafm.get_scan(subject, mod) for mod in modalities]


def hemond_data(dataset: DataSet) -> DataSet:
    scans_no_label = []
    for i, scan in enumerate(dataset):
        if not scan.has_label():
            scans_no_label.append(i)

    fraction_ts = 0.1
    n_scans = len(dataset)
    n_ts = int(fraction_ts * n_scans)
    inds = [i for i in range(n_scans)]
    random.shuffle(inds)

    for i in scans_no_label:
        inds.remove(i)
        inds.insert(0, i)

    for i in inds[:n_ts]:
        dataset[i].cond = "ts"
    for i in inds[n_ts:]:
        dataset[i].cond = "tr"

    return dataset


def lesjak():
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
