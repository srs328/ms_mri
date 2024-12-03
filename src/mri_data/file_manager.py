from __future__ import annotations

import os
import platform
import re
import copy
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Self

from attrs import define, field
from loguru import logger

from mri_data.record import Record

# ? should subid and sesid be ints instead of strs?
# ? should scan.image and scan.label be just the file names?

#! Just realized, Scan currently may not be amenable to having images that are in subdirectories of root.
#!  this is because of the use of "Path.name" in certain places like the setter for "Scan.image_path"
# TODO to fix this, use relative paths somehow


class FileLogger:
    def __init__(self):
        self.logger = logger.bind(file="")

    def log(self, level, message, file=""):
        self.logger = logger.bind(file=file)
        self.logger.log(level, message)


file_logger = FileLogger()


# ? this could be put into a config file that is loaded
drive_roots = {
    "windows": {"Data drive": "/mnt/h", "Gold SDD": "/mnt/g/Data", "default": "/mnt/h"},
    "ubuntu": {
        "smbshare": "/media/smbshare",
        "Data drive": "/media/WD_BLACK_DATA",
        "default": "/media/smbshare",
    },
}


def get_drive_root(drive="default"):
    hostname = platform.node()
    if hostname == "rhinocampus" or hostname == "ryzen9":
        return Path(drive_roots["ubuntu"][drive])
    elif hostname == "LenovoDesktop" or hostname == "srs-9-Yoga7i":
        return Path(drive_roots["windows"][drive])
    else:
        raise RuntimeError("Don't know what host this is being run on")
    

def convert_to_winroot(path: Path):
    return Path("H:/") / path.relative_to("/mnt/h")


# Right now it's unused, but could make a method in DataSet that returns a Subject object.
@dataclass
class Subject:
    name: str
    subjpath: Path
    scans: list[Path]


def path_exists(instance, attribute, value):
    if value is not None and not value.is_dir():
        print(value, attribute)
        raise ValueError(
            f"Invalid value for {attribute.name}, {value} is not a directory"
        )


def image_exists_or_none(instance, attribute, value):
    if value is None:
        return
    path = instance.root / value
    if not path.is_file():
        raise ValueError(f"Invalid value for {attribute.name}, {path} is not a file")


def parse_scan_path(path: Path | os.PathLike) -> tuple[str, str]:
    re_sub = re.compile(r"sub-ms(\d{4})")
    re_ses = re.compile(r"ses-(\d+)")
    for part in Path(path).parts:
        if match := re_sub.match(part):
            subid = match[1]
        elif match := re_ses.match(part):
            sesid = match[1]
    try:
        return subid, sesid
    except UnboundLocalError:
        return None


# validator=[image_exists_or_none] on image/label
# validator=[path_exists] on dataroot/_root
@define(slots=True, weakref_slot=False, unsafe_hash=True)
class Scan:
    subid: str = field(converter=str)
    sesid: str = field(converter=str)
    _dataroot: Path = field(converter=Path)
    _root: Path = field(default=None, converter=Path)
    image: str = field(default=None)
    label: str = field(default=None)
    cond: str = None
    id: int | None = None

    @classmethod
    def new_scan(
        cls, dataroot, subid, sesid, image=None, label=None, cond=None, subdir=""
    ) -> Self:
        root = Scan.path(dataroot, subid, sesid, subdir=subdir)
        return cls(subid, sesid, Path(dataroot), root, image, label, cond)

    def __attrs_post_init__(self):
        if self.id is None:
            self.id = int(self.subid) * int(self.sesid)
        if self._root is None:
            self._root = Scan.path(self.dataroot, self.subid, self.sesid)

    def has_label(self) -> bool:
        if self.label is not None:
            return True
        else:
            return False

    def with_root(self, dataroot) -> Self:
        new_scan = copy.deepcopy(self)
        new_scan.dataroot = dataroot
        return new_scan

    @property
    def root(self) -> Path:
        return self._root

    # TODO changing root can get sticky, the dataroot must remain the same
    @root.setter
    def root(self, root):
        self._root = root

    @property
    def dataroot(self) -> Path:
        return self._dataroot

    @dataroot.setter
    def dataroot(self, dataroot):
        relative_path = self.relative_path
        self._dataroot = dataroot
        self._root = self._dataroot / relative_path

    @property
    def image_path(self) -> Path:
        if self.image is None:
            return None
        return self.root / self.image

    @image_path.setter
    def image_path(self, path: Path | os.PathLike):
        self.image = Path(path).relative_to(self.root).name

    @property
    def label_path(self) -> Path:
        if self.label is None:
            return None
        return self.root / self.label

    @label_path.setter
    def label_path(self, path: Path | os.PathLike):
        self.label = Path(path).relative_to(self.root).name

    @property
    def relative_path(self) -> Path:
        return self.root.relative_to(self.dataroot)

    @staticmethod
    def path(dataroot, subid, sesid, subdir="") -> Path:
        return Path(dataroot) / f"sub-ms{subid}" / f"ses-{sesid}" / subdir

    def info(self) -> str:
        return f"{self.__class__.__name__}(subid={self.subid}, sesid={self.sesid})"

    @classmethod
    def _field_names(cls) -> list:
        return cls.__slots__

    def asdict(self) -> dict:
        dict_form = {k: getattr(self, k) for k in self._field_names()}
        for k, v in dict_form.items():
            if isinstance(v, Path):
                dict_form[k] = str(v)
        dict_form["root"] = dict_form.pop("_root")
        dict_form["dataroot"] = dict_form.pop("_dataroot")
        return dict_form

    @classmethod
    def from_dict(cls, dict_form) -> Self:
        for k in ["root", "image", "label", "dataroot"]:
            if dict_form[k] is not None:
                dict_form[k] = Path(dict_form[k])
        return cls(**dict_form)


@define
class Scan2(Scan):
    image: dict[str, str] = field(default=dict())
    label: dict[str, str] = field(default=dict())

    def add_image(self, key: str, name: str):
        if (self.root / name).is_file():
            self.image.update({key: name})
        else:
            raise FileNotFoundError(f"{self.root/name} does not exist")

    def add_label(self, key: str, name: str):
        if (self.root / name).is_file():
            self.label.update({key: name})
        else:
            raise FileNotFoundError(f"{self.root/name} does not exist")

    @property
    def image_path(self, key: str = None):
        if self.image is None:
            return None
        if key is not None:
            return self.root / self.image[key]
        else:
            return {k: self.root / v for k, v in self.image.items()}

    @image_path.setter
    def image_path(self, path: Path | os.PathLike, key: str = None):
        if key is not None:
            self.image[key] = Path(path).relative_to(self.root).name
        else:
            self.image = {}
        self.image = Path(path).relative_to(self.root).name


# it's a little messy changing the dataroot since I have to make sure
#   scan.root and scan.dataroot are both changed
class DataSet(Record):
    def __init__(self, dataroot, records=None):
        super().__init__(Scan, records=records)
        self._dataroot = dataroot

    @classmethod
    def dataset_like(cls, dataset: Self, keys: list[str] = None) -> Self:
        if keys is None:
            keys = []
        keys = set(keys)
        keys.update(["dataroot", "root", "subid", "sesid"])
        return cls(
            dataroot=dataset.dataroot,
            records=[{k: getattr(scan, k) for k in keys} for scan in dataset],
        )

    @classmethod
    def from_scans(cls, scans) -> Self:
        scan = scans.pop()
        dataroot = scan.dataroot
        scans.add(scan)
        return cls(dataroot=dataroot, records=[scan.asdict() for scan in scans])

    def add_images(self, image_name):
        for scan in self._records:
            scan.image = image_name

    def add_labels(self, label_name):
        for scan in self._records:
            scan.label = label_name

    def add_label(self, subid, sesid, label):
        try:
            scan = self.find_scan(subid=subid, sesid=sesid)[0]
        except LookupError:
            warnings.warn(
                f"No scan exists for subject: {subid} and session: {sesid}", UserWarning
            )
        else:
            scan.label = label

    def find_scan0(self, subid, sesid):
        sub_scans = self.retrieve(subid=subid)
        for scan in sub_scans:
            if scan.sesid == sesid:
                return scan
        # return None
        raise LookupError(
            f"No scan exists for subject: {subid} and session: {sesid}", subid, sesid
        )

    def find_scan(self, subid=None, sesid=None):
        if subid is not None and sesid is None:
            return self.retrieve(subid=subid)
        elif sesid is not None and subid is None:
            return self.retrieve(sesid=sesid)
        elif subid is not None and sesid is not None:
            sub_scans = set(self.retrieve(subid=subid))
            ses_scans = set(self.retrieve(sesid=sesid))
            scans = list(set.intersection(sub_scans, ses_scans))
            return sorted(scans, key=lambda s: (s.subid, s.sesid))
        else:
            raise TypeError("find_scan() expects at least one of 'subid' or 'sesid")

    def remove_scan(self, scan):
        idx = self.retrieve(id=scan.id, get_index=True)[0]
        del self[idx]
        self.lookup_tables = {}

    def serialize(self):
        return [scan.asdict() for scan in self]

    def sort(self, key=lambda s: s.subid):
        self._records = sorted(self, key=key)

    @property
    def dataroot(self) -> Path:
        return self._dataroot

    @dataroot.setter
    def dataroot(self, dataroot: Path):
        self._dataroot = dataroot
        for scan in self._records:
            scan.dataroot = dataroot

    def __str__(self):
        return ", ".join([str(scan) for scan in self])


def scan_3Tpioneer_bids(dataroot, image=None, label=None, subdir=None) -> DataSet:
    dataroot = Path(dataroot)

    sub_dirs = [
        Path(item.path)
        for item in os.scandir(dataroot)
        if item.is_dir() and "sub" in item.name
    ]

    dataset = DataSet(dataroot)

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


def scan_lesjak(dataroot, image=None, label=None, subdir=None) -> DataSet:
    dataroot = Path(dataroot)

    sub_dirs = [
        Path(item.path)
        for item in os.scandir(dataroot)
        if item.is_dir() and "patient" in item.name
    ]

    dataset = DataSet(dataroot)

    for i, sub_dir in enumerate(sub_dirs):
        scan_dir = sub_dir
        if subdir is not None:
            scan_dir = scan_dir / subdir

        image_file = image
        if image_file is not None and not (scan_dir / image_file).is_file():
            image_file = None

        label_file = label
        if label_file is not None and not (scan_dir / label_file).is_file():
            label_file = None
        scanid = i+1
        dataset.append(
            dict(
                id=scanid,
                subid=sub_dir.name,
                sesid=None,
                dataroot=dataroot,
                root=scan_dir,
                image=image_file,
                label=label_file,
            )
        )
        
    return dataset

# this should not be a method Scan
def find_label(scan, label_prefix: str, suffix_list: list[str] = None) -> Path:
    """find label for scan, and if there are multiple, return one
    based on priority of suffixes

    Args:
        scan (Scan): Scan for the subj+ses of interest
        label_prefix (str): prefix of the label
        suffix (list[str]): list of suffixes in order of priority
    """
    if suffix_list is None:
        suffix_list = [""]
    if "" not in suffix_list:
        suffix_list.append("")
    root_dir = scan.root
    labels = list(root_dir.glob(f"{label_prefix}*.nii.gz"))

    for suffix in suffix_list:
        label_parts = [label_prefix]
        if len(suffix) > 0:
            label_parts.append(suffix)
        logger.debug("Testing {}".format(("-".join(label_parts) + ".nii.gz").lower()))
        for lab in labels:
            logger.debug("Checking {}", lab.name.lower())
            if ("-".join(label_parts) + ".nii.gz").lower() == lab.name.lower():
                logger.debug("Found {} for {}", lab.name, scan.info())
                return lab

    logger.debug(f"No label in {[lab.name for lab in labels]} matched search")
    raise FileNotFoundError(
        f"Could not find label matching {label_prefix} "
        + f"for subject {scan.subid} ses {scan.sesid}"
    )


def nifti_name(file: Path | str) -> str:
    if isinstance(file, Path):
        file = file.name
    fileparts = file.split(".")
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

    dataset_new = DataSet(dataset.dataroot)
    for sub in subjects:
        scans = dataset.retrieve(subid=sub)
        scans_sorted = sorted(scans, key=lambda s: int(s.sesid))
        dataset_new.append(scans_sorted[0])

    return dataset_new


def filter_has_label(dataset: DataSet) -> DataSet:
    dataset_new = DataSet(dataset.dataroot)
    for scan in dataset:
        if scan.label is not None:
            dataset_new.append(scan)
    return dataset_new


def filter_has_image(dataset: DataSet) -> DataSet:
    dataset_new = DataSet(dataset.dataroot)
    for scan in dataset:
        if scan.image is not None:
            dataset_new.append(scan)
    return dataset_new


def filter_subject(dataset: DataSet) -> DataSet:
    dataset_new = DataSet(dataset.dataroot)
    for scan in dataset:
        if scan.image is not None:
            dataset_new.append(scan)
    return dataset_new


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
