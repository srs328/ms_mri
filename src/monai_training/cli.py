import click
from loguru import logger
import os
from pathlib import Path
import sys

from monai_training import preprocess, training

logger.remove(0)
logger.add(sys.stderr, level="INFO", format="{level} | {message}")

@click.group()
def cli():
    pass


@cli.command()
@click.option("-i", "--dataroot", required=True, type=str)
@click.option("-o", "--work-dir", required=True, type=str)
@click.option("-m", "--modality", required=True, multiple=True)
@click.option("-l", "--label", required=True, multiple=True)
@click.option("-f", "--filters", multiple=True)
def train(dataroot, work_dir, modality, label, filters):
    work_dir = Path(work_dir)
    if not work_dir.is_dir():
        os.makedirs(work_dir)
    logger.info("Preparing dataset")
    dataset, info = preprocess.prepare_dataset(dataroot, modality, label, filters=filters)
    preprocess.save_dataset(dataset, work_dir / "dataset.json", dataset_info=info)
    datalist_file = training.setup_training(dataset, info, work_dir)
    training.train(datalist_file)


@cli.command()
def prepare_data(dataroot):
    pass
    

if __name__ == "__main__":
    cli()


'''
monai-training train -i "/mnt/h/3TPioneer_bids" -o /home/srs-9/Projects/ms_mri/training_work_dirs/pineal_tmp" \
    -m flair -l pineal_SRS -f first_ses
'''