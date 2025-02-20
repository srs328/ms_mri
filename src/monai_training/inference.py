from loguru import logger
from pathlib import Path

from monai_training import preprocess
from mri_data.file_manager import DataSet, scan_3Tpioneer_bids, filter_first_ses


def get_inference_scans(
    dataset_train: DataSet, inference_root: Path, inference_name: str
) -> DataSet:
    dataroot = dataset_train.dataroot

    def inference_exists(dataset: DataSet) -> DataSet:
        count = 0
        dataset_new = DataSet(dataset.dataroot)
        for scan in dataset:
            if not (inference_root / scan.relative_path / inference_name).is_file():
                dataset_new.append(scan)
            else:
                count += 1
        logger.info(f"{count} scans already have inference")
        return dataset_new

    # dataset_train2 has the same subject/sessions that are in dataset_train but with a subset of the keys
    #   so that they can be compared to scans in the full data set when getting the set difference
    dataset_proc = preprocess.DataSetProcesser.new_dataset(
        dataroot, scan_3Tpioneer_bids, filters=[filter_first_ses, inference_exists]
    )
    dataset_full = dataset_proc.dataset
    dataset_train2 = DataSet.dataset_like(dataset_train, ["subid", "sesid"])
    dataset_inference = DataSet.from_scans(set(dataset_full) - set(dataset_train2))

    return dataset_inference
