# %%
import shutil
import os
from pathlib import Path
import csv
from loguru import logger
from tqdm import tqdm
import pandas as pd
from collections import defaultdict

# %%
# Custom sink that uses tqdm.write
class TqdmLoguruStream:
    def write(self, message):
        tqdm.write(message, end='')
    
    def flush(self):
        pass

logger.remove()  # Remove the default handler
logger.add(TqdmLoguruStream(), level="INFO", format="{level} | {message}")

# %%
drive_root = Path("/mnt/h")
# pioneer_bids_root = drive_root / "3Tpioneer_bids" 
pioneer_bids_root = Path("/home/srs-9/Data/ls-ai/3Tpioneer_bids")
dataroot = drive_root / "srs-9/thalamus_project/data"

datafile_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")
with open(datafile_dir / "lst_ai-sessions.csv", 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    subject_sessions = list(reader)

# %%
lesion_data = defaultdict(list)
for subid, sesid in tqdm(subject_sessions):
    lesion_data['subid'].append(int(subid))
    subject_root = pioneer_bids_root / f"sub-ms{subid}" / f"ses-{sesid}"
    # subject_root = dataroot / f"sub{subid}-{sesid}"

    lst_ai_path = subject_root / "lst-ai"
    lesion_stats = pd.read_csv(lst_ai_path / "lesion_stats.csv")
    lesion_data['total_count'].append(int(lesion_stats.Num_Lesions[0]))
    lesion_data['total_volume'].append(lesion_stats.Lesion_Volume[0])
    
    annotated_lesion_stats = pd.read_csv(lst_ai_path / "annotated_lesion_stats.csv", index_col="Region")
    for region, row in annotated_lesion_stats.iterrows():
        lesion_data[f"{region.lower()}_count"].append(int(row.Num_Lesions))
        lesion_data[f"{region.lower()}_volume"].append(row.Lesion_Volume)

# %%
lesion_data = pd.DataFrame(lesion_data, index=lesion_data['subid'])
lesion_data.to_csv(datafile_dir / "lst_ai_volumes.csv")