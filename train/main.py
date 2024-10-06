# import preprocess
# import train
# import data_file_manager as dfm
from train import cli
import json

dataroot = "/home/srs-9/Projects/ms_mri/tests/data"

dataset, info = cli.prepare_dataset(dataroot, ("flair", "t1"), "pituitary")

cli.save_dataset(dataset, "test.json", info)
