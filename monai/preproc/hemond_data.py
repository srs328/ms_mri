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

from attrs import define, field

from monai.preproc import record

PREPROC_DIR = "/home/srs-9/Projects/ms_mri/monai/preproc"
sys.path.append(PREPROC_DIR)

# even though each subject only has one scan, I'm writing this to be extensible
# for when there are multiple scans per subject

class Scan(NamedTuple):
    subid: int
    date: int
    image: Path
    label: Path

def get_subj_ses(filename):
    restr = re.compile(r"sub-ms(\d{4})_ses-(\d{8})\.nii\.gz")
    rematch = restr.match(filename)
    return rematch[1], rematch[2]


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


class HaemondData(Sequence):

    def __init__(self, basepath):
        self.basepath = Path(basepath)
        self._scans = []

    def add_scan(self, image, label, date):
        self._scans.append(Scan(subid=self.subid, date=date, image=image, label=label))   


def scan_data_dir(data_dir):
    images = [
        file.name for file in os.scandir(data_dir) if file.name.split(".")[-1] == "gz"
    ]

    dataset_paths = record.DataSet('hemond_data', Scan._fields)
    
    for image in images:
        subj, ses = get_subj_ses(image)
        scans.append(Scan(subid=subj, date=ses, image=image))

    labels = [
        file.name
        for file in os.scandir(data_dir / "labels")
        if file.name.split(".")[-1] == "gz"
    ]

    for label in labels:
        q



def scan_hemond_subjects(data_dir):
    images = [
        file.name for file in os.scandir(data_dir) if file.name.split(".")[-1] == "gz"
    ]

    image_struct = defaultdict(dict)
    for image in images:
        subj, ses = get_subj_ses(image)
        image_struct[subj].update({ses: image})

    labels = [
        file.name
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
    data_dir = Path("/mnt/t/Data/MONAI/flair")
    data, unmatched_labels = scan_hemond_subjects(data_dir)
