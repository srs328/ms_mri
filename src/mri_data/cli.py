import click
from loguru import logger
import os
from pathlib import Path

from mri_data import utils, data_file_manager

# In https://loguru.readthedocs.io/en/stable/resources/recipes.html, the section titled
# "Logging entry and exit of functions with a decorator" doesn't make sense

current_dir = Path(__file__).absolute().parent
logger.add(current_dir / "new_files.log", serialize=True, level="DEBUG")


class FileLogger:
    def __init__(self):
        self.logger = logger.bind(file="")

    def log(self, level, message, file=""):
        self.logger = logger.bind(file=file)
        self.logger.log(message, level=level)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-d", "--dataroot", type=str)
def scan_dataroot(dataroot):
    dataset = data_file_manager.scan_3Tpioneer_bids(dataroot)
    logger.info(dataset.dataroot)


@cli.command()
@click.option("-l", "--labels", nargs=2, type=str, required=True)
@click.option("-d", "--directory", type=str)
def get_dice_score(labels, directory=None):
    if directory is not None:
        paths = [os.path.join(directory, lab) for lab in labels]
    else:
        paths = labels

    img_data = [utils.load_nifti(p) for p in paths]
    dice_score = utils.dice_score(img_data[0], img_data[1])
    print(dice_score)
    return dice_score


@cli.command()
@click.option("-d", "--dataroot", type=str, required=True)
@click.option("-i", "--in", "src", type=str, required=True)
@click.option("-o", "--out", "dst", type=str, required=True)
@click.option("-f", "--script-file", type=str)
@click.option("--run-script/--no-run-script", default=False)
@click.option("--to-raise/--not-to-raise", default=True)
def rename(dataroot, src, dst, script_file, run_script, to_raise):
    dataset = data_file_manager.scan_3Tpioneer_bids(dataroot)
    kwargs = {
        "script_file": script_file,
        "run_script": run_script,
        "to_raise": to_raise,
    }

    data_file_manager.rename(dataset, src, dst, **kwargs)


if __name__ == "__main__":
    cli()
