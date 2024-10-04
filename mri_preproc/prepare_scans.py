from __future__ import annotations
import os
from pathlib import Path
import importlib
import numpy as np
import nibabel as nib
from mri_preproc.paths import data_file_manager as datafm
from mri_preproc.paths.hemond_data import DataSet
import tqdm
import random
import subprocess


def load_scan(scan_path: Path) -> np.ndarray:
    img = nib.load(scan_path)
    return np.array(img.dataobj)

# def stack_scans(subject, modalities):
#     scan_paths = [lesjak_datafm.get_scan(subject, mod) for mod in modalities]


def merge_images(image_paths, merged_path=None):
    if merged_path is None:
        image_names = [p.stem for p in image_paths]
        image_names.sort()
        merged_name = "_".join(image_names) + image_names[0].ext
        merged_path = image_paths[0].parent / merged_name
    
    image_paths = [str(p) for p in image_paths]
    cmd_parts = ["fslmerge", "-a", str(merged_path), " ".join(image_paths)]
    
    print(" ".join(cmd_parts))
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def merge_labels(label_paths, merged_path=None):
    if merged_path is None:
        label_names = [p.stem for p in label_paths]
        label_names.sort()
        merged_name = "_".join(label_names) + label_names[0].ext
        merged_path = label_paths[0].parent / merged_name
    label_paths = [str(p) for p in label_paths]
    
    label_inputs = [label_paths[0]]
    for path in label_paths[1:]:
        label_inputs.extend(["-add", path])
    cmd_parts = ["fslmaths", *label_inputs, merged_path]
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


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
