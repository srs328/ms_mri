from warnings import simplefilter

import pandas as pd

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
simplefilter(action="ignore", category=DeprecationWarning)
simplefilter(action="ignore", category=FutureWarning)

from pathlib import Path

from matplotlib import colormaps


from reload_recursive import reload_recursive
import sys

sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")
from mri_data import file_manager as fm
import helpers

reload_recursive(helpers)
import helpers


drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
data_dir = Path("/home/srs-9/Projects/ms_mri/data")



viridis = colormaps["viridis"].resampled(20)
colors = {
    "dark red1": "#eb3131",
    "light red1": "#eb7171",
    "dark blue1": "#1f4294",
    "light blue1": "#7a9df0",
    "dark green1": "#2e6023",
    "light green1": "#6dba5c",
    "dark purple1": "#8C1FA7",
    "light purple1": "#BD49DA",
    "grey6": "#707070",
    "grey5": "#6A6A6A",
    "grey4": "#5A5A5A",
    "grey3": "#4A4A4A",
    "grey2": "#3A3A3A",
    "grey1": "#333333"
}

thalamic_nuclei = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
deep_grey = [13, 14, 26, 27, 28, 29, 30, 31, 32]

thalamic_nuclei_str = [str(i) for i in thalamic_nuclei]

# presentation_cols = ["coef", ("p_fdr", "pval"), "se", "ci", "R2"]
presentation_cols = ["coef", "pval", "p_fdr", "se", "ci", "R2"]


all_predictors = [
    "LV_log",
    "CP",
    "periCSF",
    "allCSF",
    "thirdV_log",
    "fourthV_log",
    "interCSF",
    "CCF_log",
    "CCR_log",
    "CCR2_log",
    "CCF0_log",
    "periCSF_ratio_log",
    "periCSF_ratio2_log",
    "periCSF_frac_reflect_log",
    "thirdV_width",
    "THALAMUS_1",
    "medial",
    "posterior",
    "ventral",
    "anterior",
    "t2lv_log",
    "brain",
    "white",
    "grey",
    "PRL_log1p",
]

all_predictorsT = [
    "LV",
    "CP",
    "periCSF",
    "allCSF",
    "thirdV",
    "fourthV",
    "interCSF",
    "CCR",
    "CCF",
    "CCF0",
    "periCSF_ratio",
    "periCSF_frac",
    "thirdV_width",
    "THALAMUS_1",
    "medial",
    "posterior",
    "ventral",
    "anterior",
    "t2lv_log",
    "brain",
    "white",
    "grey",
    "PRL",
]

