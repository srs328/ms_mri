from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
from abc import ABC, abstractmethod
import re
import warnings

from mri_data.record import Record


# Right now it's unused, but could make a method in DataSet that returns a Subject object.
@dataclass
class Subject:
    name: str
    subjpath: Path
    scans: list[Path]


# TODO expand this to include modality
@dataclass(slots=True)
class Scan:
    subid: str
    sesid: str
    root: Path
    image: Path = None
    label: Path = None
    cond: str = None
    id: int | None = None

    def __post_init__(self):
        if self.id is None:
            self.id = int(self.subid) * int(self.sesid)

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

    @classmethod
    def _field_names(cls):
        return cls.__slots__

    @classmethod
    def from_dict(cls, dict_form):
        for k in ["root", "image", "label"]:
            if dict_form[k] is not None:
                dict_form[k] = Path(dict_form[k])
        return cls(**dict_form)

    @property
    def relative_path(self):
        return f"sub-{self.subid}/ses-{self.sesid}"


# could subclass DataSet and have initial values for things like fields and Scan as Data
# ? Does this need to be a subclass, what if the DataSet class had these two functions
# ! test if this would work with a struct other than Scan (say, namedtuple)
class DataSet(Record):

    def __init__(self, recordname: str, scan_struct, records=None):
        fields = scan_struct._field_names()
        super().__init__(recordname, fields, records=records)
        self.Data = scan_struct

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

    @property
    def dataroot(self):
        return self.Data[0].root

    def __str__(self):
        return ", ".join([str(scan) for scan in self])


def scan_3Tpioneer_bids(
    dataroot, modality=None, label=None, subdir=None, suppress_output=True
) -> DataSet:
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

            if modality is not None:
                image_path = scan_dir / f"{modality}.nii.gz"
                if not image_path.is_file():
                    image_path = None
            else:
                image_path = None
            
            if label is not None:
                label_path = scan_dir / f"{label}.nii.gz"
                if not label_path.is_file() and label is not None:
                    label_path = None
            else:
                label_path = None

            dataset.append(
                dict(
                    id=id,
                    subid=subid,
                    sesid=sesid,
                    root=ses_dir,
                    image=image_path,
                    label=label_path
                )
            )

            if not suppress_output:
                if label_path is None:
                    warnings.warn(f"No label for sub-{subid} ses-{sesid}")

    return dataset


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
    

filters = {
    "first_ses": filter_first_ses
}


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