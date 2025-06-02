from monai_training import preprocess
import subprocess
from mri_data import file_manager as fm
from tqdm import tqdm

script_file = "/home/srs-9/Projects/ms_mri/scripts/make_brainmask.sh"
dataroot = "/media/smbshare/3Tpioneer_bids"
dataset_proc = preprocess.DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids, filters=[fm.filter_first_ses])
dataset = dataset_proc.dataset
dataset.sort()

i = 0
for scan in tqdm(dataset, total=len(dataset)):
    if not (scan.root / "t1.mask.nii.gz").exists():
        i+=1
        print(scan.subid)
        cmd = ["bash", script_file, str(scan.root), "t1"]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(str(e.stderr))

print(i)