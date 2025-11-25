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





thalamic_nuclei = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
deep_grey = [13, 14, 26, 27, 28, 29, 30, 31, 32]

thalamic_nuclei_str = [str(i) for i in thalamic_nuclei]

presentation_cols = ["coef", ("p_fdr", "pval"), "se", "ci", "R2"]
presentation_cols_both_ps = ["coef", "pval", "p_fdr", "se", "ci", "R2"]


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


viridis = colormaps["viridis"].resampled(20)
colors = {
    # Grays (lighter as number increases)
    "grey1": "#333333",
    "grey2": "#3A3A3A",
    "grey3": "#4A4A4A",
    "grey4": "#5A5A5A",
    "grey5": "#6A6A6A",
    "grey6": "#707070",
    "grey7": "#8A8A8A",
    "grey8": "#A0A0A0",
    "grey9": "#C0C0C0",
    "grey10": "#E0E0E0",
    
    # Reds
    "darkest red1": "#4a0f0f",
    "darker red1": "#ad3434",
    "dark red1": "#eb3131",
    "light red1": "#eb7171",
    "darkest red2": "#4a0f0f",
    "darker red2": "#ad3434",
    "dark red2": "#db4b4b",
    "light red2": "#eb7171",
    "darkest red3": "#3d0f1f",  # More pink/magenta red
    "dark red3": "#c72e5c",
    "light red3": "#e66b92",
    
    # Blues
    "darkest blue1": "#0a1433",
    "dark blue1": "#1f4294",
    "darkish blue1": "#446cc8",
    "light blue1": "#7a9df0",
    "darkest blue2": "#0f2a35",  # Teal-ish blue
    "dark blue2": "#2E86AB",
    "light blue2": "#6DB3D4",
    
    # Greens
    "darkest green1": "#0f1f0c",
    "dark green1": "#2e6023",
    "light green1": "#6dba5c",
    "darkest green2": "#08261e",  # Teal-ish green
    "dark green2": "#1a7a5e",
    "light green2": "#4db89d",
    
    # Purples
    "darkest purple1": "#2d0a35",
    "dark purple1": "#8C1FA7",
    "light purple1": "#BD49DA",
    "darkest purple2": "#221833",  # More blue-purple
    "dark purple2": "#6B4C9A",
    "light purple2": "#9B7BC8",
    
    # Oranges
    "darkest orange1": "#402100",
    "dark orange1": "#d96b00",
    "light orange1": "#ff9d3d",
    "darkest orange2": "#3d1d00",  # Burnt orange
    "dark orange2": "#c65d00",
    "light orange2": "#e68a3d",
    
    # Teals
    "darkest teal1": "#042426",
    "dark teal1": "#0d7377",
    "light teal1": "#14b8a6",
    
    # Pinks
    "darkest pink1": "#3d142b",
    "darker pink1": "#9c2e6b",
    "dark pink1": "#c9438c",
    "light pink1": "#e778b8",
    
    # Yellows/Golds
    "darkest yellow1": "#3d3005",
    "dark yellow1": "#d4a017",
    "light yellow1": "#f4c542",
    
    # Browns
    "darkest brown1": "#2d1506",
    "dark brown1": "#8b4513",
    "light brown1": "#cd853f",
}