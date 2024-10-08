from __future__ import annotations
from attrs import define, field
from dataclasses import dataclass
import os
from pathlib import Path
import random
from abc import ABC, abstractmethod
from collections.abc import Mapping
import re
import warnings

from mri_preproc.paths.record import Record


#data_dir = "/mnt/c/Users/srs-9/OneDrive - UMass Chan Medical School/Projects/MS MRI/lesjak_2017/data"

#subjects = os.listdir(data_dir)


@dataclass
class Subject:
    name: str
    subjpath: Path
    scans: list[Path]


# TODO expand this to include modality
@dataclass(slots=True)
class Scan:
    subid: str
    date: int
    root: str
    image: Path = None
    label: Path = None
    cond: str = None

    def has_label(self):
        if self.label is not None:
            return True
        else:
            return False

    @classmethod
    def _field_names(cls):
        return cls.__slots__  

    @property
    def relative_path(self):  
        return f"sub-{self.subid}/ses-{self.date}"


# ? could this subclass Scan? nah maybe not
# ?     someone mentioned composition though
# ?     https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
# ? maybe it should because it's easier to make DataSet work if it expects a Scan or subclass
# ? right now subclassing isn't working because it doesn't inherit all the __slots__, and the only thing that shows up in __slots__ is images since it's unique to the subclass
# ?     Until I figure out how to subclass it right, I'll just copy all the methods from Scan here
@dataclass(slots=True)
class MultiModalScan(Scan):
    subid: int
    date: int
    root: str
    image: dict[str, Path] = None
    label: Path = None
    cond: str = None
    
    def has_label(self):
        if self.label is not None:
            return True
        else:
            return False

    @classmethod
    def _field_names(cls):
        return cls.__slots__
    

# could subclass DataSet and have initial values for things like fields and Scan as Data
# ? Does this need to be a subclass, what if the DataSet class had these two functions
class DataSet(Record):

    def __init__(self, recordname: str, scan_struct, records=None):
        fields = scan_struct._field_names()
        super().__init__(recordname, fields, records=records)
        self.Data: Scan = scan_struct

    def add_label(self, subid, ses, label):
        try:
            scan = self.find_scan(subid, ses)
        except LookupError:
            warnings.warn(
                f"No scan exists for subject: {subid} and session: {ses}", UserWarning
            )
        else:
            scan.label = label

    def find_scan(self, subid, ses):
        sub_scans = self.retrieve(subid=subid)
        for scan in sub_scans:
            if scan.date == ses:
                return scan
        #return None
        raise LookupError(
            f"No scan exists for subject: {subid} and session: {ses}", subid, ses
        )
        
    @property
    def dataroot(self):
        return self.Data[0].root
    

def scan_3Tpioneer_bids(dataroot, modality, label, subdir=None, suppress_output=True) -> DataSet:
    dataroot = Path(dataroot)
    sub_dirs = [Path(item.path) for item in os.scandir(dataroot) if item.is_dir() and "sub" in item.name]

    dataset = DataSet("DataSet", Scan)

    for sub_dir in sub_dirs:
        subid = re.match(r"sub-(ms\d{4})", sub_dir.name)[1]
        ses_dirs = [Path(item.path) for item in os.scandir(sub_dir) if "ses" in item.name]

        for ses_dir in ses_dirs:
            sesid = re.match(r"ses-(\d+)", ses_dir.name)[1]
            scan_dir = ses_dir
            if subdir is not None:
                scan_dir = scan_dir / subdir
            image_path = scan_dir / f"{modality}.nii.gz"
            label_path = scan_dir / f"{label}.nii.gz"
            if not image_path.is_file():
                continue
            if not label_path.is_file() and label is not None:
                continue
            
            dataset.append(
                dict(subid=subid, date=sesid, root=ses_dir, image=image_path, label=label_path)
            )

            if not suppress_output:
                if label_path is None:
                    warnings.warn(f"No label for sub-{subid} ses-{sesid}")

    return dataset


class LesjakData:
    """The LesjakData class can give the path to a NiFti given it's subject name and modality"""

    def __init__(self, basepath):
        self.basepath = Path(basepath)
        self.prefix = "SUBJECT_MODALITY.nii.gz"
        self.scan_dir = "raw"
        self.subjects = [
            item.name for item in os.scandir(self.basepath) if item.is_dir()
        ]

    def scan_name(self, subject, modality):
        name = self.prefix.replace("SUBJECT", subject)
        name = name.replace("MODALITY", modality)
        return name

    def get_scan(self, subject, modality):
        scan_name = self.scan_name(subject, modality)
        path = self.basepath / subject / self.scan_dir / scan_name
        if not path.is_file():
            raise FileNotFoundError(
                "{} does not exit".format(path.relative_to(self.basepath))
            )
        return path

    def subject_folder(self, subject):
        return self.basepath / subject

    def stacked_path(self, subject):
        path = self.basepath / subject / self.scan_dir / f"{subject}_stacked.nii.gz"


def assign_train_test(subjects, fraction_ts):
    n_subj = len(subjects)
    n_ts = int(n_subj * fraction_ts)

    random.shuffle(subjects)
    subj_ts = [(subj, "ts") for subj in subjects[:n_ts]]
    subj_tr = [(subj, "tr") for subj in subjects[n_ts:]]
    return subj_ts + subj_tr


def create_monai_dir(data, basepath: Path, modality: str):
    imagesTr_dir = basepath / "imagesTr"
    labelsTr_dir = basepath / "labelsTr"
    imagesTs_dir = basepath / "imagesTs"
    for folder in [imagesTr_dir, labelsTr_dir, imagesTs_dir]:
        os.makedirs(folder, exist_ok=True)

    #for subject in subjects:
    #    pass


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
    print("THAAAAAAAAA")
