import importlib
import os
import re
import sys
from collections import defaultdict, namedtuple
from dataclasses import dataclass, fields, asdict
from pathlib import Path
from mri_preproc.paths import hemond_data, init_paths
from mri_preproc import prepare_scans
import subprocess
import logging
from datetime import datetime

#? Why aren't errors showing up on console?
#? Could add console switches if it becomes helpful
#TODO instead of hardcoding the script paths, make them relative to this folder

logdir = '/home/srs-9/Projects/ms_mri/mri_preproc/logs'
now = datetime.now()
curr_time = now.isoformat(timespec="hours")
filename = os.path.join(logdir,f'{curr_time} processing.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(filename)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

init_paths.main()
from mri_preproc.paths.init_paths import DATA_HOME

dataset = hemond_data.collect_raw_dataset(DATA_HOME, suppress_output=True)

processing_script = "/home/srs-9/Projects/ms_mri/mri_preproc/process_flair.sh"

# register the flairs and produce affine matrices
# for data in dataset:
#     scan_dir = data.root
#     modality = "flair"
#     command_parts = [processing_script, str(scan_dir), modality, "1"]
#     try:
#         logger.info(" ".join(command_parts))
#         result = subprocess.run(command_parts, capture_output=True, text=True, check=True)
#     except subprocess.CalledProcessError as e:
#         logger.info(e.stdout)
#         logger.error(e.stderr)
#     else:
#         logger.debug(result.stdout)

processing_script = "/home/srs-9/Projects/ms_mri/mri_preproc/proc-3Tpioneer_bids/register_labels.sh"
# for i in range(3):
for data in dataset:
    # data = dataset[i]
    scan_dir = data.root
    command_parts = [processing_script, str(scan_dir), "1"]
    try:
        logger.info(" ".join(command_parts))
        result = subprocess.run(command_parts, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.info(e.stdout)
        logger.error(e.stderr)
    else:
        logger.debug(result.stdout)