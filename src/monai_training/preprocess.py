import json
import os
from pathlib import Path
from subprocess import CalledProcessError
from typing import Callable, Optional, Self

from attrs import Factory, define
from loguru import logger
from tqdm import tqdm

from mri_data import file_manager as fm
from mri_data import utils
from mri_data.file_manager import DataSet


class FileLogger:
    def __init__(self):
        self.logger = logger.bind(new_file="")

    def log(self, level, message, new_file=""):
        self.logger = logger.bind(new_file=new_file)
        self.logger.log(level, message)


file_logger = FileLogger()

# FIXME thoosl
# TODO fix so that it uses the new filtering method everywhere
@define
class DataSetProcesser:
    dataset: fm.DataSet
    image_name: str = ""
    label_name: str = ""
    modality: list[str] = Factory(list)
    label: list[str] = Factory(list)
    info: dict[str, tuple] = Factory(dict)
    suppress_exceptions: bool = False

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
        filters: list[Callable] = None,
        suppress_exceptions: bool = False,
        **kwargs,
    ) -> Self:
        dsp = cls(
            scan_func(dataroot, *args, **kwargs),
            suppress_exceptions=suppress_exceptions,
        )
        dsp.info = dict()

        if filters is not None:
            if isinstance(filters, Callable):
                filters = [filters]
            for filter in filters:
                dsp.dataset = filter(dsp.dataset)

        if all([scan.image for scan in dsp.dataset]):
            dsp.image_name = dsp.dataset[0].image
            dsp.modality = fm.parse_image_name(dsp.image_name)
            dsp.info.update(
                {"image_info": [(mod, i) for i, mod in enumerate(dsp.modality)]}
            )

        #! the labels include the initials as of now
        if all([scan.label for scan in dsp.dataset]):
            dsp.label_name = dsp.dataset[0].label
            dsp.label = fm.parse_image_name(dsp.label_name)
            dsp.info.update(
                {"label_info": [[(lab, 2**i) for i, lab in enumerate(dsp.label)]]}
            )

        return dsp

    def filter(self, filters: list[Callable], args_list: list[Optional[tuple]]):
        """filters out scans based on criteria

        Args:
            filters (list[Callable]): a list of predicate functions
            args_list (list[Optional[tuple]]): 
                a list containing the additional arguments for each function as
                tuples or None if a function takes no arguments
        """
        args_list = [arg if arg is not None else [] for arg in args_list]
        new_dataset = DataSet(self.dataset.dataroot)
        for scan in self.dataset:
            if all(
                filter_func(scan, *args)
                for filter_func, args in zip(filters, args_list)
            ):
                new_dataset.append(scan)
        self.dataset = new_dataset

    def prepare_images(self, modality: list[str] | str, log_exceptions: bool = False):
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

        dataset_copy = fm.DataSet(self.dataset.dataroot)
        for scan in tqdm(self.dataset, total=len(self.dataset)):
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
                    logger.warning("Couldn't prepare image for {}", scan.info())
                    continue
                except CalledProcessError:
                    if not self.suppress_exceptions:
                        if log_exceptions:
                            logger.exception(
                                f"Something went wrong merging images for {scan.info}"
                            )
                        else:
                            logger.error(f"Something went wrong merging images for {scan.info}")
                    continue
                    # raise
                else:
                    scan.image_path = scan.root / merged_image
                    file_logger.log(
                        "SUCCESS", f"Saved {scan.image_path}", new_file=scan.image_path
                    )
                    dataset_copy.append(scan)
                    continue

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

        dataset_copy = fm.DataSet(self.dataset.dataroot)
        for scan in tqdm(self.dataset, total=len(self.dataset)):
            if scan.label is not None:
                dataset_copy.append(scan)
                continue
            label_path = scan.root / self.label_name
            if label_path.is_file() and not suffix_list:
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
                    logger.warning("Couldn't prepare image for {}", scan.info())
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
                    scan.label_path = scan.root / fm.find_label(
                        scan, self.label[0], suffix_list=suffix_list
                    )
                except FileNotFoundError:
                    logger.warning("Couldn't prepare image for {}", scan.info())
                    continue
                else:
                    logger.info(f"Found label {scan.label} for {scan.info()}")
                    dataset_copy.append(scan)

        logger.info(f"Dataset size: {len(dataset_copy)}")
        self.dataset = dataset_copy


def save_dataset(
    dataset: DataSet, save_path: Path | os.PathLike, info: Optional[dict] = None,
    indent: Optional[int] = 4
):
    if info is None:
        info = dict()
    info.update({"dataroot": str(dataset.dataroot)})

    struct = {"info": info}
    struct.update({"data": dataset.serialize()})

    with open(save_path, "w") as f:
        json.dump(struct, f, indent=indent)


def load_dataset(path):
    with open(path, "r") as f:
        struct = json.load(f)

    # this is here till all the previously saved datasets are fixed
    struct = tmp_fix_dataset(path, struct)

    info = struct["info"]
    dataset_list = struct["data"]
    dataset = fm.DataSet(info["dataroot"], records=dataset_list)
    return dataset, info


# previously I had saved a bunch of datasets without dataroot in info.
def tmp_fix_dataset(path, struct):
    drive_root = fm.get_drive_root()
    dataroot = drive_root / "3Tpioneer_bids"

    dataset_list = struct["data"]
    dataset = fm.DataSet(dataroot, records=dataset_list)
    save_dataset(dataset, path, info=struct["info"])
    return struct


# TODO make this agnostic to whatever dataroot is in the datalist file. Change the paths
# to use the dataroot that is passed to this function
def parse_datalist(
    datalist_file: Path | os.PathLike, dataroot: Path | os.PathLike
) -> fm.DataSet:
    logger.info(f"Loading {datalist_file}")
    logger.info(f"{datalist_file} exists: {datalist_file.is_file()}")
    with open(datalist_file, "r") as f:
        datalist = json.load(f)

    dataset = fm.DataSet(dataroot)
    for scan_dict in datalist["training"]:
        subid, sesid = fm.parse_scan_path(scan_dict["image"])
        scan = fm.Scan.new_scan(
            dataroot,
            subid,
            sesid,
            image=scan_dict["image"],
            label=scan_dict["label"],
            cond="tr",
        )
        dataset.append(scan)

    for scan_dict in datalist["testing"]:
        subid, sesid = fm.parse_scan_path(scan_dict["image"])
        scan = fm.Scan.new_scan(
            dataroot,
            subid,
            sesid,
            image=scan_dict["image"],
            label=scan_dict["label"],
            cond="ts",
        )
        dataset.append(scan)

    return dataset
