import sys
import os
from pathlib import Path

from mri_data import utils
from mri_data.file_manager import scan_3Tpioneer_bids, Scan, DataSet
from monai_training import preprocess

msmri_home = Path("/home/srs-9/Projects/ms_mri")
training_work_dirs = Path("/mnt/h/training_work_dirs")

args = sys.argv[1:]

dataroot = args[0]
work_dir = args[1]
dataset_file = args[2]
