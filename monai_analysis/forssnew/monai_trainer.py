from monai.apps.auto3dseg import AutoRunner
from monai.config import print_config
import sys
from pathlib import Path
import json

work_dir = "/home/srs-9/Projects/ms_mri/training_work_dirs/forssnew3" #path to the directory where you want all the output saved
datalist_file = "/home/srs-9/Projects/ms_mri/training_work_dirs/forssnew3/datalist.json" #path to dataset.json
dataroot = "/home/srs-9/Projects/ms_mri/data/forssnew" #root directory of all the data

runner = AutoRunner(
    work_dir=work_dir,
    algos=["segresnet"],
    input={
        "modality": "MRI",
        "datalist": str(datalist_file),
        "dataroot": str(dataroot),
    },
)

with open(datalist_file, 'r') as f:
    dataset = json.load(f)

dataroot = Path(dataroot)

for file in dataset['training']:
    path = dataroot / file['image']
    check = path.exists()

max_epochs = 250

train_param = {
    "num_epochs_per_validation": 1,
    "num_images_per_batch": 2,
    "num_epochs": max_epochs,
    "num_warmup_epochs": 1,
}
runner.set_training_params(train_param)

runner.run()
