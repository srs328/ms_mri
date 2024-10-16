import errno
from loguru import logger
import nibabel as nib
import numpy as np
import os
from subprocess import run
import time
from typing import Callable, Optional

from .file_manager import Scan, nifti_name
from . import file_manager


def merge_images(image_paths, merged_path, resave=False):
    if os.path.exists(merged_path) and not resave:
        logger.debug(f"{merged_path} already exists, returning")
        return merged_path
    elif os.path.exists(merged_path) and resave:
        logger.debug(f"{merged_path} already exists, but overwriting")
    image_paths = [str(p) for p in image_paths]
    for p in image_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    cmd_parts = ["fslmerge", "-a", str(merged_path), *image_paths]

    logger.info(" ".join(cmd_parts))
    run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def merge_labels(label_paths, merged_path):
    if merged_path.is_file():
        return merged_path
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
# ! have a hacky work around for not recreating files, fix later
def combine_labels(
    scan: Scan,
    labels: list[str],
    label_id_func: Callable,
    suffix_list: Optional[list[str]] = None,
    resave=False,
) -> tuple[str, list]:
    if isinstance(labels, str) or len(labels) < 2:
        raise ValueError("Expected more than one label")

    # find files with correct prefix and suffix and assign a value for each
    logger.debug(f"Combining labels for {scan.info()}")
    base_labels = []
    label_values = []
    tmp_files = []
    for i, lab in enumerate(labels):
        base_labels.append(file_manager.find_label(scan, lab, suffix_list))
        label_values.append((lab, label_id_func(i)))

    # set the name of the combined label
    label_names = [nifti_name(base_label.name) for base_label in base_labels]
    combined_label_name = ".".join(label_names) + ".nii.gz"
    merged_label = scan.root / combined_label_name
    # return if the combined label exists already
    if merged_label.is_file() and not resave:
        return combined_label_name, label_values

    # create the combined label
    try:
        # modify each label to have the assigned value
        for lab, label_value, base_label in zip(labels, label_values, base_labels):
            tmp_filepath = scan.root / f"tmp_{lab}_{int(time.time())}.nii.gz"
            try:
                logger.debug("Trying set_label_value with", lab)
                set_label_value(base_label, tmp_filepath, label_value[1])
            except FileNotFoundError:
                logger.error("Failed set_label_value for", lab)
                raise
            else:
                logger.debug("finished setting label value")
                tmp_files.append(tmp_filepath)

        # merge the labels
        merge_labels(tmp_files, merged_label)
    except Exception:
        raise
    finally:
        # delete the temporary files
        for path in tmp_files:
            os.remove(path)

    return combined_label_name, label_values


def load_nifti(path) -> np.ndarray:
    img = nib.load(path)
    return img.get_fdata()


def dice_score(seg1, seg2):
    intersection = np.sum((seg1 > 0) & (seg2 > 0))
    volume_sum = np.sum(seg1 > 0) + np.sum(seg2 > 0)
    if volume_sum == 0:
        return 1.0
    return 2.0 * intersection / volume_sum
