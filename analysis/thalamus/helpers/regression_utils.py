from statsmodels.stats.multitest import multipletests

import pprint
from warnings import simplefilter

import pandas as pd
from IPython.display import Markdown, display
from statsmodels.stats.multitest import multipletests
from collections import defaultdict

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
import json
import re
import textwrap
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import helpers
import matplotlib.pyplot as plt
import numpy as np
import pyperclip
import statsmodels.api as sm
from statsmodels.base.wrapper import ResultsWrapper

from IPython.display import clear_output
from matplotlib import colormaps
from scipy import stats
from statsmodels.genmod.families import Poisson

from reload_recursive import reload_recursive
from statsmodels.stats.mediation import Mediation
from statsmodels.stats.outliers_influence import variance_inflation_factor
from tqdm.notebook import tqdm

from mri_data import file_manager as fm


def quick_regression(
    data, y, x, covariates=["age", "Female", "tiv"]
) -> tuple[pd.DataFrame, str]:
    """
    Returns a tuple containing statsmodels regression results and the formula of the model
    """
    exog = [x] + covariates
    formula = f"{y} ~ {' + '.join(exog)}"
    res = sm.OLS.from_formula(formula, data=data).fit()
    return res, formula


def quick_regression2(data, y, exog) -> tuple[pd.DataFrame, str]:
    """
    Returns a tuple containing statsmodels regression results and the formula of the model
    """
    formula = f"{y} ~ {' + '.join(exog)}"
    res = sm.OLS.from_formula(formula, data=data).fit()
    return res, formula


def formula_string(
    outcome: str, predictors: str | list[str], covariates: list[str] = None
):
    if isinstance(predictors, str):
        predictors = [predictors]
    if covariates is None:
        covariates = []

    independent_vars = predictors + covariates
    return f"{outcome} ~ {' + '.join(independent_vars)}"


def residualize_vars(
    model_data: pd.DataFrame, dependent_var: str, independent_vars: list[str]
) -> pd.Series:
    """
    Residualize a dependent variable by regressing out independent variables.

    Parameters:
    -----------
    model_data : pd.DataFrame
        DataFrame containing the data
    dependent_var : str
        The dependent variable to residualize
    independent_vars : list of str
        List of independent variables to regress out

    Returns:
    --------
    np.ndarray
        Residuals of the dependent variable after regression
    """
    formula = f"{dependent_var} ~ " + " + ".join(independent_vars)
    model = sm.OLS.from_formula(formula, data=model_data).fit()
    return model.resid


def run_regressions0(
    model_data: pd.DataFrame,
    outcome: str,
    predictors: list[str],
    covariates: list[str] = None,
    robust_cov: str = "HC3",
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
):
    if covariates is None:
        covariates = []

    def _get_val_by_name(obj, name, attr):
        import numpy as np

        vals = getattr(obj, attr)
        # pandas Series (has .get)
        if hasattr(vals, "get"):
            return vals.get(name, np.nan)
        # numpy array / list-like: map via model exog names
        try:
            exog_names = list(obj.model.exog_names)
        except Exception:
            exog_names = []
        if name in exog_names:
            idx = exog_names.index(name)
            try:
                return np.asarray(vals)[idx]
            except Exception:
                return np.nan
        return np.nan

    results = {}
    models = {}
    for predictor in predictors:
        independent_vars = [predictor] + covariates
        formula = f"{outcome} ~ {' + '.join(independent_vars)}"
        model = sm.OLS.from_formula(formula, model_data).fit()

        if robust_cov:
            rres = model.get_robustcov_results(cov_type=robust_cov)
        else:
            rres = model

        # confidence interval: conf_int() returns DataFrame when names available
        ci_df = rres.conf_int()
        if hasattr(ci_df, "loc") and predictor in ci_df.index:
            llci, ulci = float(ci_df.loc[predictor, 0]), float(ci_df.loc[predictor, 1])
        else:
            # fallback via exog_names -> index
            try:
                exog_names = list(rres.model.exog_names)
                idx = exog_names.index(predictor)
                ci_arr = np.asarray(ci_df)
                llci, ulci = float(ci_arr[idx, 0]), float(ci_arr[idx, 1])
            except Exception:
                llci = ulci = np.nan

        ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""
        results[predictor] = {
            "beta": _get_val_by_name(rres, predictor, "params"),
            "p_fdr": None,
            "se": _get_val_by_name(rres, predictor, "bse"),
            "llci": llci,
            "ulci": ulci,
            "ci_str": ci_str,
            "p_raw": _get_val_by_name(rres, predictor, "pvalues"),
            "R2": rres.rsquared_adj,
            "formula": formula,
        }
        models[predictor] = model

    results = pd.DataFrame(results).T

    fdr_method: str = "fdr_bh"
    fdr_alpha = 0.05
    _, p_fdr_vals, _, _ = multipletests(
        results["p_raw"], alpha=fdr_alpha, method=fdr_method
    )
    results["p_fdr"] = p_fdr_vals

    return results


# Another type of refactor would be one in which lists of exog are passed
def run_regressions(
    model_data: pd.DataFrame,
    outcomes,
    predictors,
    covariates: list = [],
    robust_cov: str = "HC3",
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
    regression_model: str = "OLS",
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[tuple, ResultsWrapper]]:
    """
    Run OLS for every (struct, predictor).
    Returns (results_by_struct, results_by_predictor)
    - results_by_struct: dict struct -> DataFrame indexed by predictor
    - results_by_predictor: dict predictor -> DataFrame indexed by struct
    Each DataFrame columns: coef, pval, se, llci, ulci, ci, R2, p_fdr, coef_sig
    """
    if covariates is None:
        covariates = []
    if isinstance(predictors, set):
        predictors = list(predictors)
    if isinstance(outcomes, str):
        outcomes = [outcomes]

    if regression_model != "OLS":
        robust_cov = False

    def _get_val_by_name(obj, name, attr):
        import numpy as np

        vals = getattr(obj, attr)
        # pandas Series (has .get)
        if hasattr(vals, "get"):
            return vals.get(name, np.nan)
        # numpy array / list-like: map via model exog names
        try:
            exog_names = list(obj.model.exog_names)
        except Exception:
            exog_names = []
        if name in exog_names:
            idx = exog_names.index(name)
            try:
                return np.asarray(vals)[idx]
            except Exception:
                return np.nan
        return np.nan

    # container: per-struct dataframes
    results_by_struct = {}
    models = defaultdict(dict)
    for struct in outcomes:
        rows = []
        for pred in predictors:
            exog = [pred] + covariates
            formula = f"{struct} ~ {' + '.join(exog)}"
            try:
                if regression_model == "OLS":
                    res = sm.OLS.from_formula(formula, data=model_data).fit()
                else:
                    res = regression_model.from_formula(formula, data=model_data).fit(disp=0)
                if robust_cov:
                    rres = res.get_robustcov_results(cov_type=robust_cov)
                else:
                    rres = res
                #* can switch to frozenset if it becomes really helpful to index without worrying about order
                models[(struct, pred)] = res
                coef = _get_val_by_name(rres, pred, "params")
                pval = _get_val_by_name(rres, pred, "pvalues")
                se = _get_val_by_name(rres, pred, "bse")

                # confidence interval: conf_int() returns DataFrame when names available
                ci_df = rres.conf_int()
                if hasattr(ci_df, "loc") and pred in ci_df.index:
                    llci, ulci = float(ci_df.loc[pred, 0]), float(ci_df.loc[pred, 1])
                else:
                    # fallback via exog_names -> index
                    try:
                        exog_names = list(rres.model.exog_names)
                        idx = exog_names.index(pred)
                        ci_arr = np.asarray(ci_df)
                        llci, ulci = float(ci_arr[idx, 0]), float(ci_arr[idx, 1])
                    except Exception:
                        llci = ulci = np.nan

                ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""
                if regression_model != "OLS":
                    r2 = ""
                else:
                    r2 = res.rsquared_adj

            except Exception as e:
                print(f"Error occurred while processing {pred} for {struct}: {e}")
                coef = pval = se = llci = ulci = np.nan
                ci_str = ""
                r2 = np.nan
                raise e
            rows.append(
                {
                    "predictor": pred,
                    "coef": coef,
                    "pval": pval,
                    "se": se,
                    "llci": llci,
                    "ulci": ulci,
                    "ci": ci_str,
                    "R2": r2,
                    "formula": formula,
                }
            )
        df_struct = pd.DataFrame(rows).set_index("predictor")
        # FDR across predictors for this struct
        pvals = df_struct["pval"].fillna(1.0).values
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        df_struct.insert(2, "p_fdr", p_fdr_vals)
        df_struct["coef_sig"] = df_struct["coef"].where(
            df_struct["p_fdr"] < fdr_alpha, 0.0
        )
        results_by_struct[struct] = df_struct

    # build results_by_predictor for compatibility
    results_by_predictor = {}
    cols = next(iter(results_by_struct.values())).columns
    for pred in predictors:
        rows = []
        for struct in outcomes:
            row = results_by_struct[struct].loc[pred].to_dict()
            row["outcome"] = struct
            rows.append(row)
        df_pred = pd.DataFrame(rows).set_index("outcome")[cols]
        pvals = df_pred["pval"].fillna(1.0).values
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        df_pred["p_fdr"] = p_fdr_vals
        df_pred["coef_sig"] = df_struct["coef"].where(
            df_struct["p_fdr"] < fdr_alpha, 0.0
        )
        results_by_predictor[pred] = df_pred

    return results_by_struct, results_by_predictor, models


def run_regressions2(
    model_data: pd.DataFrame,
    outcome: str,
    exog_list: list[list[str]],
    model_names: list[str] = None,
    covariates: list[str] = None,
    robust_cov: str = "HC3",
    regression_model: str = "OLS",
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
) -> tuple[dict[str, pd.DataFrame], dict[str, ResultsWrapper], str]:
    """
    Run OLS for one outcome on each set of variables in exog_list.
    Returns (results, models, formulas)
    - results: dict -> DataFrame indexed by model_names
    - models: dict  -> ResultsWrapper indexed by model_names
    Each DataFrame columns: coef, pval, se, llci, ulci, ci, R2, p_fdr, coef_sig
    """
    if model_names is None:
        model_names = [i for i, _ in enumerate(exog_list)]
    if covariates is None:
        covariates = []
    if regression_model != "OLS":
        robust_cov = False

    results = {}
    models = {}
    formulas = {}
    for exog, model_name in zip(exog_list, model_names):
        independent_vars = exog + covariates
        formula = f"{outcome} ~ {' + '.join(independent_vars)}"
        try:
            if regression_model == "OLS":
                    res = sm.OLS.from_formula(formula, data=model_data).fit()
            else:
                res = regression_model.from_formula(formula, data=model_data).fit(disp=0)
            if robust_cov:
                rres = res.get_robustcov_results(cov_type=robust_cov)
            else:
                rres = res
            models[model_name] = res
            coef = rres.params
            pval = rres.pvalues
            se = rres.bse
            ci_df = rres.conf_int()
            if hasattr(ci_df, "loc"):
                llci, ulci = ci_df.loc[:, 0], ci_df.loc[:, 1]
            else:
                llci, ulci = ci_df[:, 0], ci_df[:, 1]
            ci_str = [
                f"[{lci:.3}, {uci:.3}]" if not np.isnan(lci) else ""
                for lci, uci in zip(llci, ulci)
            ]
            
            try:
                r2 = res.rsquared_adj
            except AttributeError:
                r2 = ""
            exog_names = list(rres.model.exog_names)
            # confidence interval: conf_int() returns DataFrame when names available
            # ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""
        except Exception as e:
            coef = pval = se = llci = ulci = np.nan
            ci_str = ""
            r2 = np.nan
            raise e
        res_df = pd.DataFrame(
            {
                "coef": coef,
                "pval": pval,
                "se": se,
                "llci": llci,
                "ulci": ulci,
                "ci": ci_str,
                # "R2": r2,
                # "formula": formula,
            },
            index=exog_names,
        )
        results[model_name] = res_df
        formulas[model_name] = formula

    return results, models, formulas


def run_regressions3(
    model_data: pd.DataFrame,
    formula_list: list[str],
    model_names: list[str] = None,
    robust_cov: str = "HC3",
    regression_model: str = "OLS",
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
) -> tuple[dict[str, pd.DataFrame], dict[str, ResultsWrapper], str]:
    """
    Run OLS for every (struct, predictor).
    Returns (results_by_struct, results_by_predictor)
    - results_by_struct: dict struct -> DataFrame indexed by predictor
    - results_by_predictor: dict predictor -> DataFrame indexed by struct
    Each DataFrame columns: coef, pval, se, llci, ulci, ci, R2, p_fdr, coef_sig
    """
    if model_names is None:
        model_names = [i for i, _ in enumerate(formula_list)]
    if regression_model != "OLS":
        robust_cov = False

    models = {}
    results = {}
    formulas = {}
    for formula, model_name in zip(formula_list, model_names):
        try:
            if regression_model == "OLS":
                    res = sm.OLS.from_formula(formula, data=model_data).fit()
            else:
                res = regression_model.from_formula(formula, data=model_data).fit()
            if robust_cov:
                rres = res.get_robustcov_results(cov_type=robust_cov)
            else:
                rres = res
            models[model_name] = res
            coef = rres.params
            pval = rres.pvalues
            se = rres.bse
            ci_df = rres.conf_int()
            if hasattr(ci_df, "loc"):
                llci, ulci = ci_df.loc[:, 0], ci_df.loc[:, 1]
            else:
                llci, ulci = ci_df[:, 0], ci_df[:, 1]
            ci_str = [
                f"[{lci:.3}, {uci:.3}]" if not np.isnan(lci) else ""
                for lci, uci in zip(llci, ulci)
            ]

            r2 = res.rsquared_adj
            exog_names = list(rres.model.exog_names)
            # confidence interval: conf_int() returns DataFrame when names available
            # ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""
        except Exception as e:
            coef = pval = se = llci = ulci = np.nan
            ci_str = ""
            r2 = np.nan
            raise e
        res_df = pd.DataFrame(
            {
                "coef": coef,
                "pval": pval,
                "se": se,
                "llci": llci,
                "ulci": ulci,
                "ci": ci_str,
                # "R2": r2,
                # "formula": formula,
            },
            index=exog_names,
        )
        results[model_name] = res_df
        formulas[model_name] = formula

    return results, models, formulas

format_opts_ref = {
    'coef': "{:.4f}",
    'se': "{:.4f}",
    'pval': "{:.2}",  # Scientific notation
    'p_fdr': "{:.2}", 
    'R2': "{:.2}"
}

def format_df(df, format_dict):
    """Apply Styler-like formatting but output to markdown"""
    df_copy = df.copy()
    for col, fmt in format_dict.items():
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].map(lambda x: fmt.format(x))
    return df_copy


def present_model(
    model: pd.DataFrame,
    cols: list,
    inds: list = None,
    rename_index: dict = None,
    rename_cols: dict = None,
    format_opts: dict = format_opts_ref
):
    
    # cols = ["coef", ("p_fdr", "pval"), "se", "ci", "R2"]
    if inds is None:
        inds = []
    if rename_index is None:
        rename_index = {}
    if rename_cols is None:
        rename_cols = {}

    present_cols = []
    for col in cols:
        if col in model.columns:
            present_cols.append(col)
        else:
            if isinstance(col, str):
                continue
            for option in col:
                if option in model.columns:
                    present_cols.append(option)
                    break

    
    present_index = []
    for ind in inds:
        if ind in model.index:
            present_index.append(rename_index[ind])
    
    model = model.rename(index=rename_index, columns=rename_cols)
    if len(present_index) == 0:
        present_index = model.index
        
    
        
    model = format_df(model, format_opts)
    
    return model.loc[present_index, present_cols]