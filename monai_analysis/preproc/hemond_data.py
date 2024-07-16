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

from monai_analysis.preproc.record import DataSet

PREPROC_DIR = "/home/srs-9/Projects/ms_mri/monai/preproc"
sys.path.append(PREPROC_DIR)

# even though each subject only has one scan, I'm writing this to be extensible
# for when there are multiple scans per subject

# TODO expand this to include modality 
@dataclass(slots=True)
class Scan:
    subid: int
    date: int
    image: Path = None
    label: Path = None
    cond: str = None
    modality: str = None

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
        restr = re.compile(r"sub-ms(\d{4})_ses-(\d{8})\.nii\.gz")
        rematch = restr.match(filename.name)
        return rematch[1], rematch[2]


# could subclass DataSet and have initial values for things like fields and Scan as Data
class HaemondData(DataSet):

    def __init__(self, recordname: str, fields: list, records=None):
        super().__init__(recordname, fields, records=records)
        self.Data: Scan = Scan

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
        raise LookupError(
            f"No scan exists for subject: {subid} and session: {ses}", subid, ses
        )

#? would this be considered a factory function, or could it be made into one?
def scan_data_dir(data_dir) -> HaemondData:
    data_dir = Path(data_dir)
    images = [
        Path(file.path)
        for file in os.scandir(data_dir)
        if file.name.split(".")[-1] == "gz"
    ]

    dataset = HaemondData("hemond_data", Scan._field_names())

    for image in images:
        subj, ses = Scan.get_subj_ses(image)
        dataset.append(dict(subid=subj, date=ses, image=image))

    labels = [
        Path(file.path)
        for file in os.scandir(data_dir / "labels")
        if file.name.split(".")[-1] == "gz"
    ]

    for label in labels:
        subj, ses = Scan.get_subj_ses(label)
        dataset.add_label(subj, ses, label)

    return dataset


def assign_conditions(dataset: HaemondData) -> HaemondData:
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
        dataset[i].cond = 'ts'
    for i in inds[n_ts:]:
        dataset[i].cond = 'tr'
    
    return dataset


if __name__ == "__main__":
    data_dir = Path("/mnt/e/Data/Hemond/flair")
    # data, unmatched_labels = scan_hemond_subjects(data_dir)
    dataset = scan_data_dir(data_dir)
