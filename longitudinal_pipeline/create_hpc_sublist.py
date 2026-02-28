# %%
from tqdm import tqdm
import os
import shutil
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

#%%
#957402
long_sessions = pd.read_csv("/home/srs-9/Projects/ms_mri/longitudinal_pipeline/longitudinal_sessions.csv",
                            index_col="subid")

dataroot = "/home/shridhar.singh9-umw/data/longitudinal"
paths = []
for subid, row in long_sessions.iterrows():
    ses1 = int(row['ses1'])
    ses2 = int(row['ses2'])
    paths.extend([os.path.join(dataroot,f"sub{str(subid)}",str(ses1))+"\n",
                  os.path.join(dataroot, f"sub{str(subid)}", str(ses2))+"\n"])

with open("subject.txt", 'w') as f:
    f.writelines(paths)