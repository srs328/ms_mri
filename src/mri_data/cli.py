import click
import os

from . import utils

@click.group()
def cli():
    pass


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