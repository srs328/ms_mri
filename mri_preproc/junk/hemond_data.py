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

from record import Record

PREPROC_DIR = "/home/srs-9/Projects/ms_mri/monai/preproc"
sys.path.append(PREPROC_DIR)

# even though each subject only has one scan, I'm writing this to be extensible
# for when there are multiple scans per subject

#! scan_hemond_subjects is junk


@dataclass(slots=True)
class Scan:
    subid: int
    date: int
    image: Path = None
    label: Path = None

    def has_label(self):
        if self.label is not None:
            return True
        else:
            return False

    @classmethod
    def _field_names(cls):
        return [field.name for field in fields(cls)]


def get_subj_ses(filename):
    restr = re.compile(r"sub-ms(\d{4})_ses-(\d{8})\.nii\.gz")
    rematch = restr.match(filename.name)
    return rematch[1], rematch[2]


def init_scan(image):
    sub, ses = get_subj_ses(image)


class Subject:
    def __init__(self, subid):
        self.subid = subid
        self._scans = []

    def add_scan(self, image, label, date):
        self._scans.append(Scan(subid=self.subid, date=date, image=image, label=label))

    def get_scans(self):
        return self._scans

    def has_label(self):
        if self._scans.label:
            return True
        else:
            return False


# could subclass DataSet and have initial values for things like fields and Scan as Data
class HaemondData(Record):

    def __init__(self, recordname: str, fields: list, records=None):
        super().__init__(recordname, fields, records=records)
        self.Data = Scan

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


def scan_data_dir(data_dir):
    images = [
        Path(file.path)
        for file in os.scandir(data_dir)
        if file.name.split(".")[-1] == "gz"
    ]

    dataset = HaemondData("hemond_data", Scan._field_names())

    for image in images:
        subj, ses = get_subj_ses(image)
        dataset.append(dict(subid=subj, date=ses, image=image))

    labels = [
        Path(file.path)
        for file in os.scandir(data_dir / "labels")
        if file.name.split(".")[-1] == "gz"
    ]

    for label in labels:
        subj, ses = get_subj_ses(label)
        dataset.add_label(subj, ses, label)

    return dataset


def scan_hemond_subjects(data_dir):

    images = [
        Path(file.path)
        for file in os.scandir(data_dir)
        if file.name.split(".")[-1] == "gz"
    ]

    image_struct = defaultdict(dict)
    for image in images:
        subj, ses = get_subj_ses(image)
        image_struct[subj].update({ses: image})

    labels = [
        Path(file.path)
        for file in os.scandir(data_dir / "labels")
        if file.name.split(".")[-1] == "gz"
    ]

    label_struct = defaultdict(dict)
    for label in labels:
        subj, ses = get_subj_ses(label)
        label_struct[subj].update({ses: label})

    # go through all the subjects in scan_struct. get their corresponding labels
    # use pop on labels so I can see if there are any labels left without a scan
    hemond_data = []
    subjects = list(image_struct.keys())

    unmatched_labels = []
    for subject in subjects:
        subj_images = image_struct.pop(subject, {})
        subj_labels = label_struct.pop(subject, {})

        subject_struct = Subject(subject)
        sessions = list(subj_images.keys())
        for ses in sessions:
            ses_image = subj_images.pop(ses, None)
            ses_label = subj_labels.pop(ses, None)
            subject_struct.add_scan(ses_image, ses_label, ses)

        if subj_labels.values():
            unmatched_labels.extend(list(subj_labels.values()))
        hemond_data.append(subject_struct)

    for subj_labels in label_struct.values():
        if subj_labels.values():
            unmatched_labels.extend(list(subj_labels.values()))

    return hemond_data, unmatched_labels


if __name__ == "__main__":
    data_dir = Path("/mnt/e/Data/Hemond/flair")
    # data, unmatched_labels = scan_hemond_subjects(data_dir)
    dataset = scan_data_dir(data_dir)
