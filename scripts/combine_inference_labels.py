import sys

from tqdm import tqdm
from loguru import logger

from monai_training.preprocess import DataSetProcesser
from mri_data import file_manager as fm
from mri_data import utils
from mri_data.file_manager import scan_3Tpioneer_bids

logger.remove()
logger.add(sys.stderr, level="INFO")

label_names = [
    "flair.t1_choroid_resegment1_pred",
    "flair.t1_pineal1_pred",
    "t1_pituitary1_pred",
]

# it is possible to make a function to combine label_names above in a nice way
label_aliases = ["choroid_resegment1", "pineal1", "pituitary1"]


def main(inference_folder):
    drive_root = fm.get_drive_root()
    inference_root = drive_root / inference_folder

    combined_label_name = ".".join(label_aliases) + ".nii.gz"

    dataset_proc = DataSetProcesser.new_dataset(
        inference_root, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
    )
    dataset = dataset_proc.dataset
    dataset.sort()

    for scan in tqdm(dataset, total=len(dataset)):
        try:
            utils.combine_labels(
                scan,
                label_names,
                utils.power_of_two,
                combined_label_name=combined_label_name,
            )
        except FileNotFoundError as e:
            logger.error(e)
            continue


if __name__ == "__main__":
    args = sys.argv[1:]
    inference_folder = args[0]
    main(inference_folder)
