# %%
from warnings import simplefilter

import pandas as pd

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
import sys
from pathlib import Path


sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")
import utils


# %%

data_dir = Path("/home/srs-9/Projects/ms_mri/data")

# %% Load and preprocess the main clinical and MRI data

choroid_volumes = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/choroid_aschoplex_volumes.csv",
    index_col="subid",
)
ventricle_volumes = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/ventricle_volumes.csv",
    index_col="subid",
)
csf_volumes = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/csf_volumes3.csv",
    index_col="subid",
)
third_ventricle_width = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/third_ventricle_width.csv",
    index_col="subid",
)
lst_ai = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/lst_ai_volumes.csv",
    index_col="subid"
)
prl_volumes = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/prl_volumes.csv",
    index_col="subid"
)
lst_ai.rename(columns={
    "total_count": "T2LC",
    "total_volume": "T2LV",
    "periventricular_count": "periV_T2LC",
    "periventricular_volume": "periV_T2LV",
    "juxtacortical_count": "juxcort_T2LC",
    "juxtacortical_volume": "juxcort_T2LV",
    "subcortical_count": "subcort_T2LC",
    "subcortical_volume": "subcort_T2LV",
    "infratentorial_count": "infraT_T2LC",
    "infratentorial_volume": "infraT_T2LV"
}, inplace=True)

tiv = pd.read_csv("/home/srs-9/Projects/ms_mri/data/tiv_data.csv", index_col="subid")

df = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/clinical_data_processed.csv",
    index_col="subid",
)
sdmt = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/analysis/thalamus/SDMT_sheet.csv",
    index_col="subid",
)
df = df.join(
    [
        choroid_volumes,
        ventricle_volumes,
        csf_volumes,
        third_ventricle_width,
        tiv,
        lst_ai,
        prl_volumes,
        sdmt["SDMT"],
    ]
)
# some values in SDMT are strings like "need to break glass, skip"
df["SDMT"] = pd.to_numeric(df["SDMT"], errors="coerce")

# these corrections should ultimately be made to the csv file
for struct in [
    "brain",
    "cat12_brain",
    "white",
    "cat12_wm",
    "grey",
    "cat12_gm",
    "cat12_tiv",
    "thalamus",
    "t2lv",
]:
    df[struct] = df[struct] * 1000

# these three columns were normalized; dividing by vscaling un-normalizes
for struct in ["brain", "white", "grey"]:
    df[struct] = df[struct] / df['vscaling']


# %% Load HIPS-THOMAS volumes

df_thomas = utils.load_hipsthomas(data_dir)
data = df.join(df_thomas)

rename_columns = {
    "ventricle_volume": "LV",
    "choroid_volume": "CP",
    "peripheral": "periCSF",
    "all": "allCSF",
    "third_ventricle": "thirdV",
    "fourth_ventricle": "fourthV",
    "aseg_csf": "interCSF",
    "third_ventricle_width": "thirdV_width",
}
data.rename(columns=rename_columns, inplace=True)

# %% Create composite measures of CSF distribution
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

# %% Transform non-normal data
# ? See suggestions from assumption_checks.ipynb
transformations = {
    "LV": "log",
    "thirdV": "log",
    "fourthV": "log",
    "allCSF": "log",
    "periCSF": "log",
    "thirdV_width": "log",
    "interCSF": "log",
    "T2LV": "log1p",
    "periV_T2LV": "log1p",
    "juxcort_T2LV": "log1p",
    "subcort_T2LV": "log1p",
    "infraT_T2LV": "log1p",
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

data.to_csv(Path(__file__).parent / "data.csv")
# dataT.to_csv(Path(__file__).parent / "data_transformed.csv")
