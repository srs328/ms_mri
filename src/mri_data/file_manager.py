from __future__ import annotations
from attrs import define, field, validators
from collections.abc import Mapping
from dataclasses import dataclass
from loguru import logger
import os
from pathlib import Path
from abc import ABC, abstractmethod
import re
from typing import Self
from subprocess import run
import warnings

from mri_data.record import Record


# ? should subid and sesid be ints instead of strs?
# ? should scan.image and scan.label be just the file names?


class FileLogger:
    def __init__(self):
        self.logger = logger.bind(file="")

    def log(self, level, message, file=""):
        self.logger = logger.bind(file=file)
        self.logger.log(level, message)


file_logger = FileLogger()


# Right now it's unused, but could make a method in DataSet that returns a Subject object.
@dataclass
class Subject:
    name: str
    subjpath: Path
    scans: list[Path]


def path_exists(instance, attribute, value):
    if value is not None and not value.is_dir():
        raise ValueError(
            f"Invalid value for {attribute.name}, {value} is not a directory"
        )


def image_exists_or_none(instance, attribute, value):
    if value is None:
        return
    path = instance.root / value
    if not path.is_file():
        raise ValueError(f"Invalid value for {attribute.name}, {path} is not a file")


@define(slots=True, weakref_slot=False)
class Scan(Mapping):
    subid: str
    sesid: str
    dataroot: Path = field(validator=[validators.instance_of(Path), path_exists])
    root: Path = field(validator=[validators.instance_of(Path), path_exists])
    image: Path = field(default=None, validator=[image_exists_or_none])
    label: Path = field(default=None, validator=[image_exists_or_none])
    cond: str = None
    id: int | None = None

    @classmethod
    def new_scan(
        cls, dataroot, subid, sesid, image=None, label=None, cond=None, subdir=""
    ) -> Self:
        root = Scan.path(dataroot, subid, sesid, subdir=subdir)
        return cls(subid, sesid, Path(dataroot), root, image, label, cond)

    def __post_init__(self):
        if self.id is None:
            self.id = int(self.subid) * int(self.sesid)
        self.root = Path(self.root)
        self.image = Path(self.image)
        self.label = Path(self.label)
        self.dataroot = Path(self.dataroot)

    def has_label(self):
        if self.label is not None:
            return True
        else:
            return False

    def asdict(self):
        dict_form = {k: getattr(self, k) for k in self._field_names()}
        for k, v in dict_form.items():
            if isinstance(v, Path):
                dict_form[k] = str(v)
        return dict_form

    def find_label(self, label_prefix: str, suffix_list: list[str] = None) -> Path:
        """find label for scan, and if there are multiple, return one
        based on priority of suffixes

        Args:
            scan (Scan): Scan for the subj+ses of interest
            label_prefix (str): prefix of the label
            suffix (list[str]): list of suffixes in order of priority
        """
        logger.debug(f"Looking for label {label_prefix} in {self.root}")
        if suffix_list is None:
            suffix_list = [""]
        root_dir = self.root
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
            + f"for subject {self.subid} ses {self.sesid}"
        )

    @property
    def image_path(self):
        if self.image is None:
            return None
        return self.root / self.image

    @image_path.setter
    def image_path(self, path: Path | os.PathLike):
        self.image = Path(path).relative_to(self.root).name

    @property
    def label_path(self):
        if self.label is None:
            return None
        return self.root / self.label

    @label_path.setter
    def label_path(self, path: Path | os.PathLike):
        self.label = Path(path).relative_to(self.root).name

    def info(self):
        return f"{self.__class__.__name__}(subid={self.subid}, sesid={self.sesid})"

    @classmethod
    def _field_names(cls):
        return cls.__slots__

    @classmethod
    def from_dict(cls, dict_form):
        for k in ["root", "image", "label", "dataroot"]:
            if dict_form[k] is not None:
                dict_form[k] = Path(dict_form[k])
        return cls(**dict_form)

    @property
    def relative_path(self):
        return self.root.relative_to(self.dataroot)

    @staticmethod
    def path(dataroot, subid, sesid, subdir=""):
        return Path(dataroot) / f"sub-ms{subid}" / f"ses-{sesid}" / subdir

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __iter__(self):
        for key in self.__slots__:
            yield super.__getitem__(key)

    def __len__(self):
        return len(self.__slots__)


# ! test if this would work with a struct other than Scan (say, namedtuple)
# TODO DataSet and Record hierarchy and structure is pretty wonky
# scan_struct can only be scan, so no point in acting like it can take any struct
class DataSet(Record):
    def __init__(self, recordname: str, scan_struct, records=None):
        fields = scan_struct._field_names()
        super().__init__(recordname, fields, records=records)
        self.Data = scan_struct

    @classmethod
    def create_dataset(cls, recordname, scan_struct, records=None):
        if records is None:
            records = []
        # records = [scan_struct.from_dict(record) for record in records]
        return cls(recordname, scan_struct, records=records)

    def add_label(self, subid, sesid, label):
        try:
            scan = self.find_scan(subid, sesid)
        except LookupError:
            warnings.warn(
                f"No scan exists for subject: {subid} and session: {sesid}", UserWarning
            )
        else:
            scan.label = label

    def find_scan(self, subid, sesid):
        sub_scans = self.retrieve(subid=subid)
        for scan in sub_scans:
            if scan.sesid == sesid:
                return scan
        # return None
        raise LookupError(
            f"No scan exists for subject: {subid} and session: {sesid}", subid, sesid
        )

    def remove_scan(self, scan):
        idx = self.retrieve(id=scan.id, get_index=True)[0]
        del self[idx]
        self.lookup_tables = {}

    def serialize(self):
        return [scan.asdict() for scan in self]

    def sort(self, key=None):
        self._records = sorted(self, key=key)

    @property
    def dataroot(self):
        return self._records[0].dataroot

    def __str__(self):
        return ", ".join([str(scan) for scan in self])


def scan_3Tpioneer_bids(dataroot, image=None, label=None, subdir=None) -> DataSet:
    dataroot = Path(dataroot)
    sub_dirs = [
        Path(item.path)
        for item in os.scandir(dataroot)
        if item.is_dir() and "sub" in item.name
    ]

    dataset = DataSet("DataSet", Scan)

    for sub_dir in sub_dirs:
        subid = re.match(r"sub-ms(\d{4})", sub_dir.name)[1]
        ses_dirs = [
            Path(item.path) for item in os.scandir(sub_dir) if "ses" in item.name
        ]

        for ses_dir in ses_dirs:
            sesid = re.match(r"ses-(\d+)", ses_dir.name)[1]
            scan_dir = ses_dir
            if subdir is not None:
                scan_dir = scan_dir / subdir

            logger.debug(f"scan_dir: {scan_dir}")

            image_file = image
            if image_file is not None and not (scan_dir / image_file).is_file():
                image_file = None

            label_file = label
            if label_file is not None and not (scan_dir / label_file).is_file():
                label_file = None
            scanid = int(subid) * int(sesid)
            dataset.append(
                dict(
                    id=scanid,
                    subid=subid,
                    sesid=sesid,
                    dataroot=dataroot,
                    root=ses_dir,
                    image=image_file,
                    label=label_file,
                )
            )

    return dataset


def nifti_name(filename: str) -> str:
    fileparts = filename.split(".")
    if ".".join(fileparts[-2:]) != "nii.gz":
        raise ValueError("Filename does not have .nii.gz as extension")
    return ".".join(fileparts[:-2])


def parse_image_name(filename: str) -> list[str]:
    name = nifti_name(filename)
    return name.split(".")


def parse_label_parts(filename: str) -> list[tuple[str, str]]:
    labels = parse_image_name(filename)
    label_parts = []
    for label in labels:
        parts = label.split("-")
        if len(parts) > 2:
            raise ValueError(f"Cannot parse label {filename}")
        if len(parts) == 1:
            label_parts.append((parts[0], ""))
        else:
            label_parts.append((parts[0], parts[1]))
    return label_parts


def filter_first_ses(dataset: DataSet) -> DataSet:
    subjects = set()
    for scan in dataset:
        subjects.add(scan.subid)

    dataset_new = DataSet("DataSet", Scan)
    for sub in subjects:
        scans = dataset.retrieve(subid=sub)
        scans_sorted = sorted(scans, key=lambda s: int(s.sesid))
        dataset_new.append(scans_sorted[0])

    return dataset_new


def filter_has_label(dataset: DataSet) -> DataSet:
    dataset_new = DataSet("DataSet", Scan)
    for scan in dataset:
        if scan.label is not None:
            dataset_new.append(scan)
    return dataset_new


def filter_has_image(dataset: DataSet) -> DataSet:
    dataset_new = DataSet("DataSet", Scan)
    for scan in dataset:
        if scan.image is not None:
            dataset_new.append(scan)
    return dataset_new


filters = {
    "first_ses": filter_first_ses,
    "has_label": filter_has_label,
    "has_image": filter_has_image,
}


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


class Data(ABC):
    @abstractmethod
    def subjects(self):
        pass

    @abstractmethod
    def scan_name(self):
        pass

    @abstractmethod
    def scan_path(self):
        pass

    @property
    @abstractmethod
    def labels(self):
        pass

    @labels.setter
    @abstractmethod
    def labels(self):
        pass


class MonaiData:
    def __init__(self, basepath):
        self.basepath = Path(basepath)


if __name__ == "__main__":
    pass
