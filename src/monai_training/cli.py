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
@click.option("l", "--label", required=True, multiple=True)
def train(dataroot, work_dir, modality, label):
    work_dir = Path(work_dir)
    if not work_dir.is_dir():
        os.makedirs(work_dir)

    dataset, info = preprocess.prepare_dataset(dataroot, modality, label)
    preprocess.save_dataset(dataset, work_dir / "dataset.json", dataset_info=info)
    datalist_file = training.setup_training(dataset, info, work_dir)
    training.train(datalist_file)
    

if __name__ == "__main__":
    cli()