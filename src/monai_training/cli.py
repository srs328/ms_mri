import click
from loguru import logger
import os
from pathlib import Path
from subprocess import run
import sys

from monai_training import preprocess, training, inference
from monai_training.preprocess import DataSetProcesser
from mri_data import file_manager as fm
from mri_data.file_manager import scan_3Tpioneer_bids, Scan

# TODO: I can create a module mri_data.paths so that I can easily import all the paths I use

logger.remove()
logger.add(sys.stderr, level="INFO", format="{level} | {message}")

log_dir = ".logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logger.add(
    os.path.join(log_dir, "file_{time:%Y_%m_%d}.log"), rotation="6h", level="DEBUG"
)


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
    preprocess.save_dataset(dataset, work_dir / "dataset.json", info=info)
    datalist_file = training.setup_training(dataset, info, work_dir)
    training.train(datalist_file)


filter_table = {
    "first_ses": fm.filter_first_ses,
    "has_label": fm.filter_has_label,
    "has_image": fm.filter_has_image,
}


@cli.command("prepare-data")
@click.option("-i", "--dataroot", required=True, type=str)
@click.option("-m", "--modality", required=True, multiple=True)
@click.option("-l", "--label", required=True, multiple=True)
@click.option("-f", "--filters", multiple=True)
@click.option("-d", "--work-dir", type=str, required=True)
def prepare_training(dataroot, modality, label, filters, work_dir):
    logger.info("Starting")

    filters = [filter_table[filter] for filter in filters]
    print(filters)
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
    preprocess.save_dataset(dataset_proc.dataset, dataset_save, info=dataset_proc.info)

    training.setup_training(dataset_proc.dataset, dataset_proc.info, work_dir)


@cli.command()
@click.option("-i", "--dataroot", required=True, type=str)
@click.option("-d", "--inference-root", required=True, type=str)
@click.option("-f", "--label-filename", required=True, type=str)
def count_inference_labels(dataroot, inference_root, label_filename):
    dataset_proc = preprocess.DataSetProcesser.new_dataset(
        dataroot, scan_3Tpioneer_bids, filters=[fm.filter_first_ses]
    )
    dataset = dataset_proc.dataset

    inference_labels = []
    for scan in dataset:
        inference_label = inference_root / scan.relative_path / label_filename
        if inference_label.is_file():
            inference_labels.append(inference_label)
    logger.info(
        "{}/{} scans already have inference", len(inference_labels), len(dataset)
    )


@cli.command("infer")
@click.argument("config", type=click.Path(exists=True, resolve_path=True, dir_okay=False))
def infer(config):
    inference.infer(config)


# FIXME there are many conditional here, and I'm not sure what cases are unaccounted for
# TODO Find the itksnap install directory on the Ubuntu desktop
@cli.command("open-itksnap")
@click.option("--subid", type=click.STRING, required=True)
@click.option("--sesid", type=click.STRING, required=True)
@click.option("--dataroot", type=click.STRING)
@click.option("--labelroot", type=click.STRING)
@click.option(
    "-i", "--image", "images", type=click.STRING, required=True, multiple=True
)
@click.option("-s", "--seg", "labels", type=click.STRING, required=True, multiple=True)
@click.option("--inference/--not-inference", default=False)
@click.option("--win/--not-win", default=False)
@click.option("-o", "--save-dir", type=click.STRING)
def open_itksnap_workspace(
    subid, sesid, dataroot, labelroot, images, labels, inference, win, save_dir
):
    if win:
        drive_root = Path(r"H:")
        itksnap = "/mnt/c/Program Files/ITK-SNAP 4.2/bin/ITK-SNAP.exe"
        itksnap_wt = "/mnt/c/Program Files/ITK-SNAP 4.2/bin/itksnap-wt.exe"
    else:
        drive_root = fm.get_drive_root()
        itksnap = "itksnap"
        itksnap_wt = "itksnap-wt"

    if dataroot is None:
        dataroot = drive_root / "3Tpioneer_bids"

    if labelroot is None:
        if not inference:
            labelroot = dataroot
        else:
            labelroot = drive_root / "3Tpioneer_bids_predictions"

    scan = Scan.new_scan(dataroot, subid, sesid)
    inference = scan.with_root(labelroot)

    image_paths = [str((scan.root) / image) for image in images]
    label_paths = [str(scan.with_root(labelroot).root / label) for label in labels]

    command = [f"'{itksnap}'", "-g"]
    command.extend(" -o ".join(image_paths).split(" "))
    command.append("-s")
    command.extend(" -s ".join(label_paths).split(" "))

    click.echo(" ".join(command))

    # top line doesn't work, see cli-notes.md
    #// run(command, shell=True)
    run(["/bin/bash", "-c", " ".join(command)])

    if save_dir:
        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            os.makedirs(save_dir)
        save_path = save_dir / f"sub-{subid}-ses{sesid}.itksnap"
        if not save_path.is_file():
            command = [f"'{itksnap_wt}'", "-layers-set-main"]
            command.extend(" -layers-add-anat ".join(image_paths).split(" "))
            command.append("-layers-add-seg")
            command.extend(" -layers-add-seg ".join(label_paths).split(" "))
            command.extend(["-o", save_path])
            
            click.echo(" ".join(command))
            run(["/bin/bash", "-c", " ".join(command)])


if __name__ == "__main__":
    cli()
