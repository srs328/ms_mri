import json
from loguru import logger
from subprocess import CalledProcessError

from mri_data import data_file_manager as dfm
from mri_data import utils


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
                utils.combine_labels(scan, label, label_name)
            except FileNotFoundError:
                continue
            except CalledProcessError:
                logger.error("Something went wrong merging labels")
                raise
            else:
                scan.label = scan.root / label_name
                logger.success(f"Saved {scan.label}")

        if scan.image is None and len(modality) > 1:
            base_images = [scan.root / f"{mod}.nii.gz" for mod in modality]
            merged_image = scan.root / image_name
            try:
                utils.merge_images(base_images, merged_image)
            except FileNotFoundError:
                continue
            except CalledProcessError:
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