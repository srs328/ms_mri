from warnings import simplefilter

import pandas as pd

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
simplefilter(action="ignore", category=DeprecationWarning)
simplefilter(action="ignore", category=FutureWarning)

import re
import textwrap
from pathlib import Path
from pyprocessmacro import Process

import numpy as np
import pyperclip
import statsmodels.api as sm
from matplotlib import colormaps
from scipy import stats
from IPython.display import Markdown, display
from io import StringIO
import matplotlib.pyplot as plt


from reload_recursive import reload_recursive
import sys

sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")
from mri_data import file_manager as fm
import helpers

import regression_utils


reload_recursive(regression_utils)
reload_recursive(helpers)
import helpers
from helpers import load_df, zscore, get_colors
from regression_utils import (
    quick_regression,
    quick_regression2,
    residualize_vars,
    run_regressions,
)


drive_root = fm.get_drive_root()
dataroot = drive_root / "3Tpioneer_bids"
data_dir = Path("/home/srs-9/Projects/ms_mri/data")



viridis = colormaps["viridis"].resampled(20)
colors = helpers.get_colors()

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
    "asegCSF",
    "CCF_log",
    "CCR_log",
    "CCF0_log",
    "periCSF_ratio_log",
    "periCSF_frac_square",
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
    "asegCSF",
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

