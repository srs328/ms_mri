from __future__ import annotations

import os
import random
import re
import sys
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
from pprint import pprint

from attrs import define, field, asdict
from dataclasses import dataclass, fields
import warnings

from mri_preproc.paths.record import Record

# PREPROC_DIR = "/home/srs-9/Projects/ms_mri/monai/preproc"
# sys.path.append(PREPROC_DIR)

# even though each subject only has one scan, I'm writing this to be extensible
# for when there are multiple scans per subject

# ? If I have multiple modalities things get tricky. One approach would be that for each session
# ?  there are multiple Scans, one for each modality and one for a label (then I'd restructure Scan)
# ?  A second approach is that there would still be separate Scan objects for each modality, but each one
# ?  would have the same label as the label attribute of Scan
# ?  A third approach is making a new Scan struct that holds all modalities in it


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

    @staticmethod
    def get_subj_ses(filename):
        restr = re.compile(r"sub-(ms\d{4})_ses-(\d{8})\.nii\.gz")
        rematch = restr.match(filename.name)
        return rematch[1], rematch[2]


# ? could this subclass Scan? nah maybe not
# ?     someone mentioned composition though
# ?     https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
# ? maybe it should because it's easier to make DataSet work if it expects a Scan or subclass
# ? right now subclassing isn't working because it doesn't inherit all the __slots__, and the only thing that shows up in __slots__ is images since it's unique to the subclass
# ?     Until I figure out how to subclass it right, I'll just copy all the methods from Scan here
@dataclass(slots=True)
class MultiModalScan:
    subid: int
    date: int
    root: str
    images: dict[str, Path] = None
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

    @staticmethod
    def get_subj_ses(filename):
        restr = re.compile(r"sub-(ms\d{4})_ses-(\d{8})\.nii\.gz")
        rematch = restr.match(filename.name)
        return rematch[1], rematch[2]


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


# ? this is a function that could be fed into a factory function to produce a concrete instance. for another dataset I'd make another function to collect the data
def scan_data_dir(dataroot) -> DataSet:
    dataroot = Path(dataroot)
    images = [
        Path(file.path)
        for file in os.scandir(dataroot)
        if file.name.split(".")[-1] == "gz"
    ]

    dataset = DataSet("hemond_data", Scan)

    for image in images:
        subj, ses = Scan.get_subj_ses(image)
        dataset.append(dict(subid=subj, date=ses, root=dataroot, image=image))

    labels = [
        Path(file.path)
        for file in os.scandir(dataroot / "labels")
        if file.name.split(".")[-1] == "gz"
    ]

    for label in labels:
        subj, ses = Scan.get_subj_ses(label)
        dataset.add_label(subj, ses, label)

    return dataset


# kinda confusing how I have to reconstruct each path, and then how in the scan loop, suddenly its looping
#   over full paths. change the outer loops to use item.path instead
#? should I add a try except block to skip directories that aren't subject dirs?
def collect_raw_dataset(dataroot, suppress_output=False) -> DataSet:
    dataroot = Path(dataroot)
    sub_dirs = [Path(item.path) for item in os.scandir(dataroot) if item.is_dir() and "sub" in item.name]
    modalities = ["flair", "phase", "t1", "t1_gd"]

    dataset = DataSet("DataSet", MultiModalScan)

    for sub_dir in sub_dirs:
        subid = re.match(r"sub-(ms\d{4})", sub_dir.name)[1]
        ses_dirs = [Path(item.path) for item in os.scandir(sub_dir) if "ses" in item.name]

        for ses_dir in ses_dirs:
            sesid = re.match(r"ses-(\d+)", ses_dir.name)[1]
            scan_paths = ses_dir.glob("*.nii.gz")

            image_dict = defaultdict(Path)
            label = None
            for scan_path in scan_paths:
                scan_prefix = re.match(r"(.+)\.nii\.gz", scan_path.name)[1]
                if scan_prefix in modalities:
                    image_dict[scan_prefix] = scan_path
                elif "lesion_index" in scan_prefix:
                    label = scan_path

            if not suppress_output:
                pprint(f"For sub-{subid} ses-{sesid} found:")
                pprint(list(image_dict.keys()))
                if label is None:
                    warnings.warn(f"No label for sub-{subid} ses-{sesid}")

            dataset.append(
                dict(subid=subid, date=sesid, root=ses_dir, images=image_dict, label=label)
            )

    return dataset

def collect_proc_dataset(dataroot, suppress_output=True) -> DataSet:
    dataroot = Path(dataroot)
    sub_dirs = [Path(item.path) for item in os.scandir(dataroot) if item.is_dir() and "sub" in item.name]
    modality = "flair"

    dataset = DataSet("DataSet", Scan)

    for sub_dir in sub_dirs:
        subid = re.match(r"sub-(ms\d{4})", sub_dir.name)[1]
        ses_dirs = [Path(item.path) for item in os.scandir(sub_dir) if "ses" in item.name]

        for ses_dir in ses_dirs:
            sesid = re.match(r"ses-(\d+)", ses_dir.name)[1]
            proc_dir = ses_dir / "proc"
            image_path = proc_dir / "flair-brain-mni_reg.nii.gz"
            label_path = proc_dir / "lesion_index.t3m20-mni_reg.nii.gz"
            if not image_path.is_file():
                continue
            if not label_path.is_file():
                label_path = None
            
            dataset.append(
                dict(subid=subid, date=sesid, root=ses_dir, image=image_path, label=label_path)
            )

            if not suppress_output:
                if label_path is None:
                    warnings.warn(f"No label for sub-{subid} ses-{sesid}")

    return dataset


def assign_conditions(dataset: DataSet) -> DataSet:
    scans_no_label = []
    for i, scan in enumerate(dataset):
        if not scan.has_label():
            scans_no_label.append(i)

    fraction_ts = 0.1
    n_scans = len(dataset)
    n_ts = int(fraction_ts * n_scans)
    inds = [i for i in range(n_scans)]
    random.shuffle(inds)

    for i in scans_no_label:
        inds.remove(i)
        inds.insert(0, i)

    for i in inds[:n_ts]:
        dataset[i].cond = "ts"
    for i in inds[n_ts:]:
        dataset[i].cond = "tr"

    return dataset


if __name__ == "__main__":
    # data_dir = Path("/mnt/t/Data/3Tpioneer_bids")
    data_dir = Path("/mnt/t/Data/MONAI/flair")
    dataset = scan_data_dir(data_dir)
    # dataset = collect_raw_dataset(data_dir, suppress_output=True)
    # data, unmatched_labels = scan_hemond_subjects(data_dir)
    # dataset = scan_data_dir(data_dir)
    thoo = 4
