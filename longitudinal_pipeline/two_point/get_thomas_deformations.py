# %%
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

# %%
subject_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv", index_col="subid")
# dataroot = Path("/home/shridhar.singh9-umw/data/longitudinal")
dataroot = Path("/home/srs-9/hpc/data/longitudinal")

