import click
from loguru import logger
import os
from pathlib import Path
import sys

from monai_training import preprocess, training
from monai_training.preprocess import DataSetProcesser
from mri_data.file_manager import scan_3Tpioneer_bids

logger.remove()
logger.add(sys.stderr, level="INFO", format="{level} | {message}")


@click.group()
def cli():
    pass


@cli.command()
@click.option("-o", "--work-dir", type=str, required=True)
@click.option("-d", "--datalist-file", type=str)
@click.option("-i", "--dataroot", type=str)
@click.option("-m", "--modality", multiple=True)
@click.option("-l", "--label", multiple=True)
@click.option("-f", "--filters", multiple=True)
def train(work_dir, datalist_file, dataroot, modality, label, filters):
    work_dir = Path(work_dir)
    if not work_dir.is_dir():
        os.makedirs(work_dir)

    if datalist_file is not None:
        training.train(work_dir / datalist_file)
        return

    logger.info("Preparing dataset")
    dataset, info = preprocess.prepare_dataset(
        dataroot, modality, label, filters=filters
    )
    preprocess.save_dataset(dataset, work_dir / "dataset.json", dataset_info=info)
    datalist_file = training.setup_training(dataset, info, work_dir)
    training.train(datalist_file)


@cli.command("prepare-data")
@click.option("-i", "--dataroot", required=True, type=str)
@click.option("-m", "--modality", required=True, multiple=True)
@click.option("-l", "--label", required=True, multiple=True)
@click.option("-f", "--filters", multiple=True)
@click.option("-d", "--work-dir", type=str, required=True)
def prepare_training(dataroot, modality, label, filters, work_dir):
    logger.info("Starting")
    dataset_proc = DataSetProcesser.new_dataset(
        dataroot, scan_3Tpioneer_bids, filters=filters
    )
    dataset_proc.prepare_labels(label, ["CH", "SRS", "ED", "DT"], resave=True)
    dataset_proc.prepare_images(modality)

    dataset_proc.dataset.sort(key=lambda s: s.subid)
    logger.info(f"Dataset size: {len(dataset_proc.dataset)}")

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    dataset_save = os.path.join(work_dir, "dataset.json")
    preprocess.save_dataset(
        dataset_proc.dataset, dataset_save, dataset_info=dataset_proc.info
    )

    training.setup_training(dataset_proc.dataset, dataset_proc.info, work_dir)


if __name__ == "__main__":
    cli()


"""
monai-training train -i "/mnt/h/3TPioneer_bids" -o /home/srs-9/Projects/ms_mri/training_work_dirs/pineal_tmp" \
    -m flair -l pineal_SRS -f first_ses

monai-training prepare-data -i "/media/hemondlab/Data1/3Tpioneer_bids" -m flair -l pineal_SRS -f first_ses
"""
