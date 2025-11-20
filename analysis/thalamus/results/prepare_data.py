# %%
from warnings import simplefilter

import pandas as pd

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
import sys
from pathlib import Path

# import helpers
from matplotlib import colormaps

sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")
from utils import load_df
import utils

from mri_data import file_manager as fm

#%%
drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
data_dir = Path("/home/srs-9/Projects/ms_mri/data")
fig_path = Path(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/figures_tables/choroid_associations"
)

df = load_df()
df_thomas = utils.load_hipsthomas(data_dir)

data = df.join(df_thomas)

# these corrections should ultimately be made to the csv file
for struct in ["brain", "white", "grey", "thalamus", "t2lv"]:
    data[struct] = data[struct] * 1000

#%%
# /home/srs-9/Projects/ms_mri/analysis/thalamus/helpers/helpers.py:225: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
#   df["CCF0"] = df["LV"] / df["allCSF"]
# /home/srs-9/Projects/ms_mri/analysis/thalamus/helpers/helpers.py:226: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor pe

# maybe print a log of what what composited 
def composite_vars(df):
    df["CCF0"] = df["LV"] / df["allCSF"]
    df["CCF"] = df["LV"] / (df["LV"] + df["periCSF"])
    df["CCF2"] = (df["LV"] + df["thirdV"]) / (df["LV"] + df["thirdV"] + df["periCSF"])
    df["CCR"] = df["LV"] / df["periCSF"]
    df["CCR2"] = (df["LV"] + df["thirdV"]) / df["periCSF"]
    df["periCSF_ratio"] = df["periCSF"] / df["LV"]
    df["periCSF_ratio2"] = df["periCSF"] / (df["LV"] + df["thirdV"])
    df["periCSF_frac"] = df["periCSF"] / df["allCSF"]
    df["thirdV_expansion"] = df['thirdV_width'] / df['thirdV']
    
    # Produce central measures from normalized versions
    LV_norm = df["LV"] / df["LV"].mean()
    thirdV_norm = df["thirdV"] / df["thirdV"].mean()
    centralV_norm = (df["LV"] + df["thirdV"]) / (df["LV"] + df["thirdV"]).mean()
    periCSF_norm = df["periCSF"] / df["periCSF"].mean()
    
    df["CCF_norm"] = LV_norm / (LV_norm + periCSF_norm)
    df["CCF2_norm"] = (LV_norm + thirdV_norm) / (LV_norm + thirdV_norm + periCSF_norm)
    df["CCR_norm"] = LV_norm / periCSF_norm
    df["CCR2_norm"] = centralV_norm / periCSF_norm
    df["CCR2_norm2"] = (LV_norm + thirdV_norm) / periCSF_norm
    df["periCSF_ratio_norm"] = periCSF_norm / LV_norm
    df["periCSF_ratio2_norm"] = periCSF_norm / centralV_norm    
    df["periCSF_ratio2_norm2"] = periCSF_norm / (LV_norm + thirdV_norm)    
    return df

data = composite_vars(data)

#%%
#! See suggestions from assumption_checks.ipynb
# TODO It would be helpful if the transformed variable name was general so I
# TODO     wouldnt have to remember which transform was applied to each
transformations = {
    "LV": "log",
    "thirdV": "log",
    "fourthV": "log",
    "allCSF": "log",
    "periCSF": "log",
    "thirdV_width": "log",
    "interCSF": "log",
    "t2lv": "log",
    "PRL": "log1p",
    "CCR": "log",
    "CCR2": "log",
    "CCF": "log",
    "CCF2": "log",
    "CCF0": "log",
    "periCSF_ratio": "log",
    "periCSF_ratio2": "log",
    "periCSF_frac": "reflect_log",
    "THALAMUS_1": "log",
    "CCR_norm": "log",
    "CCR2_norm": "log",
    "CCR2_norm2": "log",
    "CCF_norm": "log",
    "CCF2_norm": "log",
    "periCSF_ratio_norm": "log",
    "periCSF_ratio2_norm": "log",
    "periCSF_ratio2_norm2": "log",
}
data = utils.transform_variables(data, transformations)
# dataT = utils.transform_variables(data, transformations, rename=False)


viridis = colormaps["viridis"].resampled(20)
colors = utils.get_colors()

MS_patients = data["dz_type2"] == "MS"
NONMS_patients = data["dz_type2"] == "!MS"
NIND_patients = data["dz_type5"] == "NIND"
OIND_patients = data["dz_type5"] == "OIND"
RMS_patients = data["dz_type5"] == "RMS"
PMS_patients = data["dz_type5"] == "PMS"


thalamic_nuclei = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
deep_grey = [13, 14, 26, 27, 28, 29, 30, 31, 32]

thalamic_nuclei_str = [str(i) for i in thalamic_nuclei]

hips_thomas_ref = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/hipsthomas_struct_index.csv", index_col="index"
)["struct"]
hips_thomas_invref = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/hipsthomas_struct_index.csv", index_col="struct"
)["index"]

data.to_csv(Path(__file__).parent / "data.csv")
# dataT.to_csv(Path(__file__).parent / "data_transformed.csv")
