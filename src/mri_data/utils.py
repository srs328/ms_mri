import errno
from loguru import logger
import nibabel as nib
import numpy as np
import os
from pathlib import Path
from subprocess import run
import sys
import time
from typing import Callable, Optional

from .data_file_manager import Scan, nifti_name

logger.remove()
logger.add(sys.stderr, level="INFO")


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
) -> tuple[str, list]:
    if isinstance(labels, str) or len(labels) < 2:
        raise ValueError("Expected more than one label")

    logger.debug(f"Combining labels for {scan.info()}")
    label_names = []
    label_values = []
    tmp_files = []
    for i, lab in enumerate(labels):
        base_label = find_label(scan, lab, suffix_list)
        label_names.append(nifti_name(base_label.name))
        combined_label_name = ".".join(label_names) + ".nii.gz"
        merged_label = scan.root / combined_label_name
        label_values.append((lab, 2**i))

    if merged_label.is_file():
        return combined_label_name, label_values

    try:
        for i, lab in enumerate(labels):
            base_label = find_label(scan, lab, suffix_list)
            label_names.append(nifti_name(base_label.name))
            tmp_filepath = scan.root / f"tmp_{lab}_{int(time.time())}.nii.gz"
            try:
                logger.debug("Trying set_label_value with", lab)
                set_label_value(base_label, tmp_filepath, label_id_func(i))
            except FileNotFoundError:
                logger.error(print("Failed set_label_value for", lab))
                raise
            else:
                logger.debug("finished setting label value")
                tmp_files.append(tmp_filepath)
                label_values.append((lab, 2**i))

        merge_labels(tmp_files, merged_label)
    except Exception:
        raise
    finally:
        for path in tmp_files:
            os.remove(path)

    return combined_label_name, label_values


def find_label(scan: Scan, label_prefix: str, suffix_list: list[str] = None) -> Path:
    """find label for scan, and if there are multiple, return one
    based on priority of suffixes

    Args:
        scan (Scan): Scan for the subj+ses of interest
        label_prefix (str): prefix of the label
        suffix (list[str]): list of suffixes in order of priority
    """
    logger.debug(f"Looking for label {label_prefix} in {scan.root}")
    if suffix_list is None:
        suffix_list = [""]
    root_dir = scan.root
    labels = list(root_dir.glob(f"{label_prefix}*.nii.gz"))

    for suffix in suffix_list:
        label_parts = [label_prefix]
        if len(suffix) > 0:
            label_parts.append(suffix)
        for lab in labels:
            if ("-".join(label_parts) + ".nii.gz").lower() == lab.name.lower():
                return lab

    logger.debug(f"No label in {[lab.name for lab in labels]} matched search")
    raise FileNotFoundError(
        f"Could not find label matching {label_prefix} "
        + f"for subject {scan.subid} ses {scan.sesid}"
    )


def load_nifti(path) -> np.ndarray:
    img = nib.load(path)
    return img.get_fdata()


def dice_score(seg1, seg2):
    intersection = np.sum((seg1 > 0) & (seg2 > 0))
    volume_sum = np.sum(seg1 > 0) + np.sum(seg2 > 0)
    if volume_sum == 0:
        return 1.0
    return 2.0 * intersection / volume_sum


def rename(dataset, src, dst, script_file=None, run_script=False, to_raise=True):
    """
    takes a DataSet object and saves bash script to rename any file named src
    in each scan's root dir to dst. This function itself makes no changes to the
    file system of the dataset

    Args:
        dataset (DataSet): DataSet object containing scans' paths
        src (str): name of file to rename
        dst (str): name of new file
        script_file (str, optional): relative or absolute path to save rename
            script to. Defaults to None.
    """
    rename_commands = ["#" + "!/bin/sh", ""]
    for scan in dataset:
        # smbShare paths are case insensitive, so need to compare to exact string
        if scan.subid == "1191":
            print("thoo")
        if src in os.listdir(scan.root):
            src_path = scan.root / src
            dst_path = scan.root / dst
            if dst_path.is_file():
                if to_raise:
                    raise FileExistsError
                else:
                    continue
            rename_commands.append(f"mv {src_path} {dst_path}")

    if script_file is None:
        script_file = "tmp/rename_commands.sh"
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
    with open(script_file, "w") as f:
        f.writelines([cmd + "\n" for cmd in rename_commands])
    if run_script:
        run(["chmod", "+x", script_file])
        run(script_file)
