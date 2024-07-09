from __future__ import annotations
from attrs import define, field
from dataclasses import dataclass
import os
from pathlib import Path
import random
from abc import ABC, abstractmethod
from collections.abc import Mapping


data_dir = "/mnt/c/Users/srs-9/OneDrive - UMass Chan Medical School/Projects/MS MRI/lesjak_2017/data"

subjects = os.listdir(data_dir)


@dataclass
class Subject:
    name: str
    subjpath: Path
    scans: list[Path]


class LesjakData:
    """The LesjakData class can give the path to a NiFti given it's subject name and modality
    """
    def __init__(self, basepath):
        self.basepath = Path(basepath)
        self.prefix = "SUBJECT_MODALITY.nii.gz"
        self.scan_dir = "raw"
        self.modalities = ["FLAIR", "T1W", "T1WKS", "T2W"]
        self.subjects = self.get_subjects()

    def get_subjects(self):
        subjects = dict()
        subject_fileobjs = [item for item in os.scandir(self.basepath) if item.is_dir()]
        subjects["name"] = [item.name for item in subject_fileobjs]
        subjects["path"] = {item.name: Path(item.path) for item in subject_fileobjs}
        return subjects

    def create_subject(name):
        pass

    def scan_name(self, subject, modality):
        name = self.prefix.replace("SUBJECT", subject)
        name = name.replace("MODALITY", modality)
        return name

    def scan_path(self, subject, modality):
        scan_name = self.scan_name(subject, modality)
        path = self.subjects["path"][subject] / self.scan_dir / scan_name
        if not path.is_file():
            raise FileNotFoundError(
                "{} does not exit".format(path.relative_to(self.basepath))
            )
        return path


def assign_train_test(subjects, fraction_ts):
    n_subj = len(subjects)
    n_ts = n_subj * int(fraction_ts)

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

    for subject in subjects:
        pass


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
