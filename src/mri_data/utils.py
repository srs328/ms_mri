import errno
from loguru import logger
import nibabel as nib
import numpy as np
import os
from pathlib import Path
from subprocess import run
import time
from typing import Callable, Optional
from nipype.interfaces import fsl
from skimage.metrics import hausdorff_distance
from medpy.metric.binary import hd95
import logging
import csv

from .file_manager import Scan, nifti_name
from . import file_manager

logging.getLogger("nipype.interface").setLevel(logging.CRITICAL)


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
    label_paths = [str(p) for p in label_paths]
    for p in label_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    logger.debug("Merging labels: {}", label_paths)
    label_inputs = [label_paths[0]]
    for path in label_paths[1:]:
        label_inputs.extend(["-add", path])
    cmd_parts = ["fslmaths", *label_inputs, merged_path]
    run(cmd_parts, check=True, stderr=True, stdout=True)
    logger.debug("Merged label is: {}", merged_path)
    return merged_path


def set_label_value(label_path, output_path, val):
    logger.debug("thoo0")
    if not os.path.isfile(label_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), label_path)
    if not os.path.isdir(os.path.dirname(output_path)):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_path)

    logger.debug("thoo1")
    cmd_parts = [
        "fslmaths",
        str(label_path),
        "-bin",
        "-mul",
        str(val),
        str(output_path),
    ]
    logger.debug(" ".join(cmd_parts))
    run(cmd_parts, check=True)
    logger.debug("thoo4")
    return output_path


def combine_labels(
    scan: Scan,
    labels: list[str],
    label_id_func: Callable,
    suffix_list: Optional[list[str]] = None,
    combined_label_name: Optional[str] = None,
    resave=False,
) -> tuple[str, list]:
    if isinstance(labels, str) or len(labels) < 2:
        raise ValueError("Expected more than one label")

    # find files with correct prefix and assign a value for each
    logger.info(f"Combining labels for {scan.info()}")
    base_labels = []
    label_values = []
    tmp_files = []
    for i, lab in enumerate(labels):
        base_labels.append(file_manager.find_label(scan, lab, suffix_list))
        label_values.append((lab, label_id_func(i)))

    # set the name of the combined label
    if combined_label_name is None:
        label_names = [nifti_name(base_label.name) for base_label in base_labels]
        combined_label_name = ".".join(label_names) + ".nii.gz"

    merged_label = scan.root / combined_label_name
    # return if the combined label exists already
    if merged_label.is_file() and not resave:
        logger.debug("{} exists", merged_label)
        return combined_label_name, label_values

    # create the combined label
    try:
        # modify each label to have the assigned value
        for lab, lab_val, base_lab in zip(labels, label_values, base_labels):
            tmp_filepath = scan.root / f"tmp_{lab}_{int(time.time())}.nii.gz"
            try:
                logger.debug("Setting {} with id {}", lab, lab_val[1])
                set_label_value(base_lab, tmp_filepath, lab_val[1])
                logger.debug("thoo")
            except FileNotFoundError:
                logger.error("Failed set_label_value for {}", lab)
                raise
            else:
                tmp_files.append(tmp_filepath)

        # merge the labels
        merge_labels(tmp_files, merged_label)
    except Exception:
        raise
    finally:
        logger.success("Saved combined label to {}", merged_label)
        # delete the temporary files
        for path in tmp_files:
            os.remove(path)
            logger.debug("Removed temporary file {}", path.name)

    return combined_label_name, label_values


# function for assigning id's to labels
def power_of_two(i: int) -> int:
    return 2**i


def load_nifti(path) -> np.ndarray:
    img = nib.load(path)
    return img.get_fdata()


def dice_score(seg1, seg2, seg1_val=1, seg2_val=1):
    intersection = np.sum((seg1 == seg1_val) & (seg2 == seg2_val))
    volume_sum = np.sum(seg1 == seg1_val) + np.sum(seg2 == seg2_val)
    if volume_sum == 0:
        # ? Why did I originally make this 1.0? Was there good reason, or mistake?
        # return 1.0
        return None
    return 2.0 * intersection / volume_sum


def iou(seg1, seg2, seg1_val=1, seg2_val=1):
    intersection = np.sum((seg1 == seg1_val) & (seg2 == seg2_val))
    union = np.sum((seg1 == seg1_val) | (seg2 == seg2_val))
    if union == 0:
        return 1.0
    return intersection / union


def hausdorff_dist(seg1, seg2, seg1_val=1, seg2_val=1):
    seg1_fix = np.zeros_like(seg1)
    seg1_fix[seg1 == seg1_val] = 1
    seg2_fix = np.zeros_like(seg2)
    seg2_fix[seg2 == seg2_val] = 1
    return hd95(seg1_fix, seg2_fix)


def compute_volume(path, index_mask_file=None, terminal_output="none"):
    # Create an instance of the ImageStats interface
    stats = fsl.ImageStats()

    # Specify the input image
    stats.inputs.in_file = path
    if index_mask_file is not None:
        stats.inputs.index_mask_file = index_mask_file

    # Define the operations you want to perform
    stats.inputs.op_string = "-V"  # Calculate mean and volume

    # stats.terminal_output = terminal_output

    # Run the interface
    result = stats.run()

    return result.outputs.out_stat


def create_itksnap_workspace_cmd(label_scan, image_scan, save_dir):
    label_path = file_manager.convert_to_winroot(label_scan.label_path)
    image_names = file_manager.parse_image_name(image_scan.image)
    label_root = Path(label_scan.root)
    image_root = Path(image_scan.root)

    image_paths = [(image_root / name).with_suffix(".nii.gz") for name in image_names]
    image_paths = [file_manager.convert_to_winroot(p) for p in image_paths]

    main_image = "-layers-set-main {} -tags-add {}-MRI".format(
        image_paths[0], image_names[0].upper()
    )
    extra_images = " ".join(
        [
            "-layers-add-anat {} -tags-add {}-MRI".format(path, name.upper())
            for path, name in zip(image_paths[1:], image_names[1:])
        ]
    )
    seg = "-layers-add-seg {} -tags-add {}".format(
        label_path, nifti_name(label_scan.label)
    )

    save_path = os.path.join(
        save_dir, f"sub-ms{label_scan.subid}-ses-{label_scan.sesid}.itksnap"
    )
    save = f"-o {save_path}"

    command_parts = ["itksnap-wt.exe", main_image, extra_images, seg, save]
    command = " ".join(command_parts)
    # run(command)
    return command


def open_itksnap_workspace_cmd(images: list[str], labels: list[str] = None, win=False):
    if images is None:
        raise Exception("No images")
    if labels is None:
        labels = []
    if win:
        images = [file_manager.convert_to_winroot(Path(p)) for p in images]
        labels = [file_manager.convert_to_winroot(Path(p)) for p in labels]
    images = [str(p) for p in images]
    labels = [str(p) for p in labels]
    command = ["itksnap"]
    command.extend(["-g", images[0]])
    # command.extend(" ".join(["-o {}".format(im) for im in images[1:]]).split(" "))
    if len(images) > 1:
        command.append("-o")
        command.extend(images[1:])
    if len(labels) > 0:
        command.append("-s")
        command.extend(labels)
    return " ".join(command)

def fsleyes_cmd(images: list[str], 
                labels: list[str] = None, 
                outlines: list[str] = None):
    
    if images is None:
        images = []
    if labels is None:
        labels = []
    if outlines is None:
        outlines = []
    images = [str(p) for p in images]
    labels = [str(p) for p in labels]
    outlines = [str(p) for p in outlines]

    command = ["fsleyes"]
    command.extend(images)
    for label in labels:
        command.extend([label, "-ot", "label", "-l", "freesurfercolorlut"])
    for outline in outlines:
        command.extend([outline, "-ot", "label", "-o"])
    
    return " ".join(command)


