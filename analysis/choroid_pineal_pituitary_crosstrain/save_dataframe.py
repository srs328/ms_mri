import pandas as pd

import nibabel as nib

from loguru import logger
from pathlib import Path
from tqdm import tqdm

from mri_data import file_manager as fm
from mri_data import utils
from monai_training.preprocess import DataSetProcesser

#! change so it saves in curr dir

logger.remove()

drive_root = fm.get_drive_root()
msmri_home = Path("/home/srs-9/Projects/ms_mri")
training_work_dirs = msmri_home / "training_work_dirs"
dataroot = drive_root / "3Tpioneer_bids"
clinical_data_root = drive_root / "Secure_Data" / "Large"
project_dataroot = msmri_home / "data"


keep_cols = ["ms_type", "flair_contrast", "sex", "age", "tiv"]
df_full = pd.read_csv(project_dataroot / "clinical_data_full.csv", index_col="subid")
df_full = df_full[keep_cols]
df_full.index.name = "subject_id"
try:
    df_full.insert('dz_type', df_full['ms_type'])
except Exception:
    pass

df_full.loc[:, 'dz_type'] = df_full['ms_type']

df_full.loc[df_full['ms_type'] == 'CIS', 'dz_type'] = 'RRMS'
df_full.loc[df_full['ms_type'].isin(['PPMS', 'SPMS', 'RPMS', 'PRMS']), 'dz_type'] = 'PMS'
df_full.loc[df_full['ms_type'].isin(['NIND', 'OIND', 'HC']), 'dz_type'] = '!MS'

df_full.loc[:, 'dz_type2'] = df_full['dz_type']
df_full.loc[df_full['dz_type'].isin(['RRMS', 'PMS']), 'dz_type2'] = 'MS'

work_dir_names = ["choroid_pineal_pituitary3", "choroid_pineal_pituitary3-2", "choroid_pineal_pituitary3-3", "choroid_pineal_pituitary3-4"]
work_dirs = [training_work_dirs / name / "ensemble_output" for name in work_dir_names]
ensemble_datasets = [fm.scan_3Tpioneer_bids(work_dir, label="flair.t1_ensemble.nii.gz") for work_dir in work_dirs]

subjects = []
for dataset in ensemble_datasets:
    for scan in dataset:
        subjects.append(int(scan.subid))

def has_subject(scan, subjects: list[int]) -> bool:
    if int(scan.subid) in subjects:
        return True
    else:
        return False
    

orig_dataset_proc = DataSetProcesser.new_dataset(dataroot, fm.scan_3Tpioneer_bids, filters=fm.filter_first_ses)
orig_dataset_proc.filter([has_subject], [(subjects,)])
orig_dataset_proc.prepare_labels(["choroid_t1_flair", "pineal", "pituitary"], ["CH", "SRS", "DT", "ED"])
orig_dataset = orig_dataset_proc.dataset


auto_segs = {}
for dataset in ensemble_datasets:
    for scan in dataset:
        auto_segs[scan.subid] = scan.label_path

man_segs = {}
for scan in orig_dataset:
    man_segs[scan.subid] = scan.label_path


df = df_full.loc[subjects, :]

df = df_full[df_full.index.isin(subjects)]
for subid, _ in df.iterrows():
    df.loc[subid, ('manual_label',)] = man_segs[str(subid)]
    df.loc[subid, ('auto_label',)] = auto_segs[str(subid)]

for scan in orig_dataset:
    df.loc[int(scan.subid), ('scan_folder',)] = scan.root


def get_volumes(path):
    vol_stats = utils.compute_volume(path, index_mask_file=path)
    
    return tuple([stat[1] for stat in vol_stats])


for subid, _ in tqdm(df.iterrows()):
    try:
        man_vol = get_volumes(df.loc[subid, 'manual_label'])
    except Exception:
        print(scan.subid)
        continue
    try:
        assert len(man_vol) == 3
    except AssertionError:
        man_vol = [None, None, None]

    df.loc[subid, ['choroid_vol_man', 'pineal_vol_man', 'pituitary_vol_man']] = man_vol


    try:
        auto_vol = get_volumes(df.loc[subid, 'auto_label'])
    except Exception:
        print(subid)
        continue
    try:
        assert len(auto_vol) == 3
    except AssertionError:
        auto_vol = [None, None, None]
    
    df.loc[subid, ['choroid_vol_auto', 'pineal_vol_auto', 'pituitary_vol_auto']] = auto_vol


def get_dice_scores(label1, label2):
    seg1 = nib.load(label1).get_fdata()
    seg2 = nib.load(label2).get_fdata()
    choroid = utils.dice_score(seg1, seg2, seg1_val=1, seg2_val=1)
    pineal = utils.dice_score(seg1, seg2, seg1_val=2, seg2_val=2)
    pituitary = utils.dice_score(seg1, seg2, seg1_val=3, seg2_val=3)
    return choroid, pineal, pituitary


for subid, _ in df.iterrows():
    df.loc[subid, ['choroid_dice', 
                    'pineal_dice', 
                    'pituitary_dice']] = get_dice_scores(df.loc[subid, 'auto_label'], 
                                                        df.loc[subid, 'manual_label'])


df.to_csv("dataframe.csv")
