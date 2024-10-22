import functools

# from mri_preproc.paths.data_file_manager import Scan
from pathlib import Path
from loguru import logger
import re
import shutil

from monai_training.preprocess import DataSetProcesser
from monai_training import preprocess
from mri_data import file_manager as fm

dataroot = Path("/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids")

# print(Scan._field_names)


def pretty_sumab(func):
    def inner(a, b):
        print(str(a) + " + " + str(b) + " is ", end="")
        return func(a, b)

    return inner


@pretty_sumab
def sumab(a, b):
    summed = a + b
    print(summed)
    return summed


def f(a, b, /, **kwargs):
    print(a, b, kwargs)


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            print(name)
            print(kwargs)
            result = func(*args, **kwargs)
            return result

        return wrapped

    return wrapper


@logger_wraps()
def foo(a, b, c, **kwargs):
    print("Inside the function")
    return a * b * c


def process_dataset():
    current_dir = Path(__file__).absolute().parent
    logger.add(current_dir / "new_files.log", serialize=True, level="DEBUG")
    modality = ["t1", "flair"]
    label = ["pineal", "choroid_t1_flair", "pituitary"]
    suffix_list = ["CH", "SRS", ""]
    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels(label, suffix_list)
    dataset_proc.prepare_images(modality)
    re_image = re.compile(r"flair.t1")
    for scan in dataset_proc.dataset:
        print(scan.image)
        assert re_image.match(scan.image)
        assert scan.image_path.is_file()


def test_multilabel():
    root = Path(dataroot) / "sub-ms1010" / "ses-20180208"
    label_names = ["foo", "bar", "baz"]
    for lab in label_names:
        dst_path = root / f"{lab}.nii.gz"
        shutil.copy(root / "lesion_index.t3m20.nii.gz", dst_path)

    dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids)
    dataset_proc.prepare_labels(label_names)
    dataset_proc.prepare_images("flair")
    assert len(dataset_proc.dataset) == 1
    assert (
        dataset_proc.dataset[0].label_path
        == dataset_proc.dataset[0].root / "bar_baz_foo.nii.gz"
    )


def modify_dict(thee):
    thee["thoop"]["bar"] = "baz"


def check_dct_behavior():
    a_dict = dict()
    a_dict["thoop"] = {}
    print(a_dict)
    modify_dict(a_dict)
    print(a_dict)


if __name__ == "__main__":
    # test_multilabel()
    dataset, info = preprocess.load_dataset("/home/hemondlab/Projects/ms_mri/training_work_dirs/pineal1/training-dataset.json")
