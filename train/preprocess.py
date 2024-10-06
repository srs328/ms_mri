import errno
from loguru import logger
import os
import subprocess
import time

# I had added return_on_error but then realized it is probably not necessary. delete once sure


def merge_images(image_paths, merged_path):
    image_paths = [str(p) for p in image_paths]
    for p in image_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    cmd_parts = ["fslmerge", "-a", str(merged_path), *image_paths]

    logger.info(" ".join(cmd_parts))
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
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
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
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
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
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


image_path = "/mnt/e/3Tpioneer_bids/sub-ms1001/ses-20170215/pituitary_practice.nii.gz"
val = 4
output_path = "/mnt/e/3Tpioneer_bids/sub-ms1001/ses-20170215/thoop.nii.gz"
