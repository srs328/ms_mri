from monai_training import preprocess
import subprocess
from mri_data import file_manager as fm

script_file = "/home/srs-9/Projects/ms_mri/scripts/make_brainmask.sh"
dataroot = "/media/smbshare/3Tpioneer_bids"
dataset_proc = preprocess.DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids, filters=[fm.filter_first_ses])
dataset = dataset_proc.dataset
dataset.sort()

for scan in dataset:
    cmd = ["sh", script_file, str(scan.root), "t1"]
    subprocess.run(cmd)