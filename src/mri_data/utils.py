import errno
from loguru import logger
import nibabel as nib
import numpy as np
import os
from pathlib import Path
from subprocess import run
import time

from .data_file_manager import Scan


def merge_images(image_paths, merged_path):
    image_paths = [str(p) for p in image_paths]
    for p in image_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    cmd_parts = ["fslmerge", "-a", str(merged_path), *image_paths]

    logger.info(" ".join(cmd_parts))
    run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def merge_labels(label_paths, merged_path):
    label_paths = [str(p) for p in label_paths]
    for p in label_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    label_inputs = [label_paths[0]]
    for path in label_paths[1:]:
        label_inputs.extend(["-add", path])
    cmd_parts = ["fslmaths", *label_inputs, merged_path]
    run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def set_label_value(label_path, output_path, val):
    if not os.path.isfile(label_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), label_path)
    if not os.path.isdir(os.path.dirname(output_path)):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_path)

    cmd_parts = [
        "fslmaths",
        str(label_path),
        "-bin",
        "-mul",
        str(val),
        str(output_path),
    ]
    run(cmd_parts, check=True, stderr=True, stdout=True)
    return output_path


# return a tuple that gives the value for each label name
def combine_labels(scan, labels, combined_label_name):
    if isinstance(labels, str) or len(labels) < 2:
        raise ValueError("Expected more than one label")

    label_values = set()
    tmp_files = []
    for i, lab in enumerate(labels):
        base_label = scan.root / f"{lab}.nii.gz"
        tmp_filepath = scan.root / f"tmp_{lab}_{int(time.time())}.nii.gz"
        try:
            # print("Trying set_label_value with", lab)
            set_label_value(base_label, tmp_filepath, 2**i)
        except Exception:
            # print("Failed set_label_value for", lab)
            for path in tmp_files:
                os.remove(path)
            tmp_files = []
            raise
        else:
            # print("finished setting label value")
            tmp_files.append(tmp_filepath)
            label_values.add((lab, 2**i))

    merged_label = scan.root / combined_label_name
    merge_labels(tmp_files, merged_label)

    for path in tmp_files:
        os.remove(path)

    return label_values


def find_label(scan: Scan, label_prefix: str, suffix_list: list[str]) -> Path:
    """find label for scan, and if there are multiple, return one 
    based on priority of suffixes

    Args:
        scan (Scan): Scan for the subj+ses of interest
        label_prefix (str): prefix of the label
        suffix (list[str]): list of suffixes in order of priority
    """
    root_dir = scan.root
    labels = list(root_dir.glob(f"{label_prefix}*.nii.gz"))

    for suffix in suffix_list:
        print(suffix)
        for lab in labels:
            print(lab.stem)
            if (label_prefix + suffix + ".nii.gz").lower() == lab.name.lower():
                return lab
    
    logger.debug(f"No label in {[lab.name for lab in labels]} matched search")
    raise FileNotFoundError


def load_nifti(path) -> np.ndarray:
    img = nib.load(path)
    return img.get_fdata()


def dice_score(seg1, seg2):
    intersection = np.sum((seg1 > 0) & (seg2 > 0))
    volume_sum = np.sum(seg1 > 0) + np.sum(seg2 > 0)
    if volume_sum == 0:
        return 1.0
    return 2.0 * intersection / volume_sum