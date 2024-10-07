import errno
import json
from loguru import logger
import os
from subprocess import run, CalledProcessError
import time

from train import data_file_manager as dfm


# later make the label use a glob in case there are initials after label name
def prepare_dataset(dataroot, modality, label):
    if isinstance(modality, str):
        modality = [modality]
    if len(modality) > 1:
        modality = list(modality)
        modality.sort()
        image_name = "_".join(modality) + ".nii.gz"
        image_ids = [(mod, i) for i, mod in enumerate(modality)]
    else:
        image_name = f"{modality[0]}.nii.gz"
        image_ids = [(modality[0], 0)]

    if isinstance(label, str):
        label = [label]
    if len(label) > 1:
        label = list(label)
        label.sort()
        label_name = "_".join(label) + ".nii.gz"
        # ? combine_labels() returns label_ids, idk if I should set that here or then
        label_ids = [(lab, 2**i) for i, lab in enumerate(label)]
    else:
        label_name = f"{label[0]}.nii.gz"
        label_ids = [(label[0], 1)]  #! this might not always be true, revisit

    dataset = dfm.scan_3Tpioneer_bids(dataroot, modality, label)
    dataset_copy = dfm.DataSet("DataSet", dfm.Scan)
    for scan in dataset:
        if scan.label is None and len(label) > 1:
            try:
                combine_labels(scan, label, label_name)
            except FileNotFoundError as e:
                continue
            except CalledProcessError as e:
                logger.error("Something went wrong merging labels")
                raise
            else:
                scan.label = scan.root / label_name
                logger.success(f"Saved {scan.label}")

        if scan.image is None and len(modality) > 1:
            base_images = [scan.root / f"{mod}.nii.gz" for mod in modality]
            merged_image = scan.root / image_name
            try:
                merge_images(base_images, merged_image)
            except FileNotFoundError as e:
                continue
            except CalledProcessError as e:
                logger.error("Something went wrong merging images")
                raise
            else:
                scan.image = scan.root / merged_image
                logger.success(f"Saved {scan.image}")

        dataset_copy.append(scan)

    dataset_info = {"image_info": image_ids, "label_info": label_ids}

    return dataset_copy, dataset_info


def save_dataset(dataset, save_path, dataset_info=None):
    struct = {"info": dataset_info}
    struct.update({"data": dataset.serialize()})

    with open(save_path, "w") as f:
        json.dump(struct, f, indent=4)


def load_dataset(path):
    with open(path, "r") as f:
        struct = json.load(f)

    info = struct["info"]
    dataset_list = struct["data"]
    dataset = dfm.DataSet("DataSet", dfm.Scan, records=dataset_list)
    return dataset, info


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


def set_label_value(image_path, output_path, val):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), image_path)
    if not os.path.isdir(os.path.dirname(output_path)):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_path)

    cmd_parts = [
        "fslmaths",
        str(image_path),
        "-bin",
        "-mul",
        str(val),
        str(output_path),
    ]
    run(cmd_parts, check=True, stderr=True, stdout=True)
    return output_path


# return a tuple that gives the value for each label name
def combine_labels(scan, labels, label_name):
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

    merged_label = scan.root / label_name
    merge_labels(tmp_files, merged_label)

    for path in tmp_files:
        os.remove(path)

    return label_values
