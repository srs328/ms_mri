import pandas as pd
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
from pathlib import Path
import json
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime
import re
from scipy import stats
from scipy.optimize import curve_fit
import numpy as np
import statsmodels.api as sm
from matplotlib import colormaps
from tqdm.notebook import tqdm
import helpers
from sklearn.metrics import r2_score
from IPython.display import clear_output
import textwrap
from statsmodels.stats.outliers_influence import variance_inflation_factor

# from reload_recursive import reload_recursive
from statsmodels.stats.mediation import Mediation
from statsmodels.genmod.families import Poisson
import pyperclip

from mri_data import file_manager as fm


from statsmodels.regression.linear_model import RegressionResultsWrapper

model_data = df_z[MS_patients]

outcome = "LV_logtrans"
predictors = [
    "CP",
    "periCSF",
    "allCSF",
    "thirdV",
    "thirdV_width",
    "THALAMUS1",
    "medial",
    "posterior",
    "ventral",
    "anterior",
    "brain",
    "white",
    "grey"
]

covariates = "age + Female + tiv"
results = {}
for predictor in predictors:
    formula = f"{outcome} ~ {predictor} + {covariates}"
    model: RegressionResultsWrapper = sm.OLS.from_formula(formula, model_data).fit()
    model.
    results[predictor] = {
        'beta': model.params[predictor],
        'p': model.params[predictor],
        'se': model.
    }
    model.