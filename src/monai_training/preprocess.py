from attrs import define, Factory
import json
from loguru import logger
import os
from subprocess import CalledProcessError
from tqdm import tqdm
from typing import Callable, Self

from mri_data import file_manager as dfm
from mri_data import utils


class FileLogger:
    def __init__(self):
        self.logger = logger.bind(new_file="")

    def log(self, level, message, new_file=""):
        self.logger = logger.bind(new_file=new_file)
        self.logger.log(level, message)


file_logger = FileLogger()


@define
class DataSetProcesser:
    dataset: dfm.DataSet
    image_name: str = ""
    label_name: str = ""
    modality: list[str] = Factory(list)
    label: list[str] = Factory(list)
    info: dict[str, tuple] = Factory(dict)

    # ? won't worry about filters for now
    #! two ways I approach write factory function, idk which to go with (see notes)
    @classmethod
    def new_dataset0(cls, dataroot, scan_func):
        return cls(scan_func(dataroot))

    # TODO figure out how to handle label initials from parse_label_name()
    # TODO   will need to use it during the label exists check (if label_path.is_file():)
    # TODO use tqdm
    @classmethod
    def new_dataset(
        cls,
        dataroot: str | os.PathLike,
        scan_func: Callable,
        *args,
        filters=None,
        **kwargs,
    ) -> Self:
        dsp = cls(scan_func(dataroot, *args, **kwargs))
        dsp.info = dict()

        if filters is not None:
            if isinstance(filters, str):
                filters = [filters]
            for filter in filters:
                dsp.dataset = dfm.filters[filter](dsp.dataset)

        if all([scan.image for scan in dsp.dataset]):
            dsp.image_name = dsp.dataset[0].image
            dsp.modality = dfm.parse_image_name(dsp.image_name)
            dsp.info.update(
                {"image_info": [(mod, i) for i, mod in enumerate(dsp.modality)]}
            )

        #! the labels include the initials as of now
        if all([scan.label for scan in dsp.dataset]):
            dsp.label_name = dsp.dataset[0].label
            dsp.label = dfm.parse_image_name(dsp.label_name)
            dsp.info.update(
                {"label_info": [[(lab, 2**i) for i, lab in enumerate(dsp.label)]]}
            )

        return dsp

    def prepare_images(self, modality: list[str] | str):
        logger.info("Prepare Images")
        if isinstance(modality, str):
            self.modality = [modality]
        else:
            self.modality = modality
        if len(self.modality) > 1:
            self.modality = list(self.modality)
            self.modality.sort()
            self.image_name = ".".join(self.modality) + ".nii.gz"
            image_ids = [(mod, i) for i, mod in enumerate(self.modality)]
        else:
            self.image_name = f"{self.modality[0]}.nii.gz"
            image_ids = [(self.modality[0], 0)]
        self.info.update({"image_info": image_ids})

        dataset_copy = dfm.DataSet()
        for scan in self.dataset:
            if scan.image is not None:
                dataset_copy.append(scan)
                continue
            image_path = scan.root / self.image_name
            if image_path.is_file():
                scan.image_path = image_path
                dataset_copy.append(scan)
                continue
            if len(self.modality) > 1:
                base_images = [scan.root / f"{mod}.nii.gz" for mod in modality]
                merged_image = scan.root / self.image_name
                try:
                    utils.merge_images(base_images, merged_image)
                except FileNotFoundError:
                    continue
                except CalledProcessError:
                    logger.error("Something went wrong merging images")
                    raise
                else:
                    scan.image_path = scan.root / merged_image
                    file_logger.log(
                        "SUCCESS", f"Saved {scan.image_path}", new_file=scan.image_path
                    )
                    dataset_copy.append(scan)

        self.dataset = dataset_copy

    def prepare_labels(
        self,
        label: list[str] | str,
        suffix_list: list[str] = None,
        id_label: Callable = lambda i: i,
        resave=False,
    ):
        logger.info("Prepare Labels")
        if isinstance(label, str):
            self.label = [label]
        else:
            self.label = label
        if len(self.label) > 1:
            self.label = list(self.label)
            self.label.sort()
            self.label_name = ".".join(self.label) + ".nii.gz"
            # ? combine_labels() returns label_ids, idk if I should set that here or then
            label_ids = [(lab, id_label(i)) for i, lab in enumerate(self.label)]
            logger.debug(self.label_name)
        else:
            self.label_name = f"{self.label[0]}.nii.gz"
            label_ids = [(self.label[0], 1)]  #! this might not always be true, revisit
        self.info.update({"label_info": label_ids})

        dataset_copy = dfm.DataSet()
        for scan in self.dataset:
            if scan.label is not None:
                dataset_copy.append(scan)
                continue
            label_path = scan.root / self.label_name
            if label_path.is_file():
                logger.debug(f"Label {label_path.name} exists")
                scan.label_path = label_path
                dataset_copy.append(scan)
                continue
            if len(self.label) > 1:
                logger.debug(f"Need to create {self.label_name}")
                try:
                    this_label_name, _ = utils.combine_labels(
                        scan,
                        self.label,
                        id_label,
                        suffix_list=suffix_list,
                        resave=resave,
                    )
                except FileNotFoundError:
                    continue
                except CalledProcessError:
                    logger.error("Something went wrong merging labels")
                    raise
                else:
                    scan.label_path = scan.root / this_label_name
                    file_logger.log(
                        "SUCCESS", f"Saved {scan.label_path}", new_file=scan.label_path
                    )
                    dataset_copy.append(scan)
            else:
                try:
                    scan.label_path = scan.root / dfm.find_label(
                        scan, self.label[0], suffix_list=suffix_list
                    )
                except FileNotFoundError:
                    continue
                else:
                    logger.info(f"Found label {scan.label} for {scan.info()}")
                    dataset_copy.append(scan)

        logger.info(f"Dataset size: {len(dataset_copy)}")
        self.dataset = dataset_copy


def power_of_two(i: int) -> int:
    return 2**i


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
    dataset = dfm.DataSet(records=dataset_list)
    return dataset, info


# later make the label use a glob in case there are initials after label name
def prepare_dataset(dataroot, modality, label, filters=None, suffix_list=None):
    count = 0
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

    dataset_info = {"image_info": image_ids, "label_info": label_ids}

    file_logger.log("DEBUG", "Starting scan_3Tpioneer_bids()")
    dataset = dfm.scan_3Tpioneer_bids(dataroot, image_name, label_name)

    file_logger.log("DEBUG", f"Filters: {[filter for filter in filters]}")
    if filters is not None:
        for filter in filters:
            dataset = dfm.filters[filter](dataset)

    if len(modality) == 1 and len(label) == 1:
        dataset = dfm.filter_has_image(dataset)
        dataset = dfm.filter_has_label(dataset)
        if len(dataset) == 0:
            raise Exception("Empty dataset")
        logger.info(
            f"Collected dataset with images: {image_name} and labels: {label_name}, size: {len(dataset)}"
        )
        return dataset, dataset_info

    logger.info(f"Creating images: {image_name} and labels: {label_name}")
    dataset_copy = dfm.DataSet("DataSet", dfm.Scan)
    for scan in tqdm(dataset):
        if count > 200:
            break
        count += 1
        if scan.label is None and len(label) > 1:
            try:
                utils.combine_labels(scan, label, label_name, suffix_list=suffix_list)
            except FileNotFoundError:
                continue
            except CalledProcessError:
                logger.error("Something went wrong merging labels")
                raise
            else:
                scan.label = scan.root / label_name
                file_logger.log("SUCCESS", f"Saved {scan.label}", new_file=scan.label)

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
                file_logger.log("SUCCESS", f"Saved {scan.image}", new_file=scan.image)

        dataset_copy.append(scan)

    if len(dataset_copy) == 0:
        raise Exception("Empty dataset")

    logger.info(
        f"Collected dataset with images: {image_name} and labels: {label_name}, size: {len(dataset)}"
    )
    return dataset_copy, dataset_info
