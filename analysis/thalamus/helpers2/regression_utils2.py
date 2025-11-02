from warnings import simplefilter

import pandas as pd
from statsmodels.stats.multitest import multipletests

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

import numpy as np
import statsmodels.api as sm



def quick_regression(y, x, data, covariates=None):
    if covariates is None:
        covariates = ["age", "Female", "tiv"]
    exog = [x] + covariates
    formula = f"{y} ~ {' + '.join(exog)}"
    res = sm.OLS.from_formula(formula, data=data).fit()
    return res, formula


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
        formula = f"{outcome} ~ {" + ".join(independent_vars)}"
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


def run_regressions(
    model_data: pd.DataFrame,
    outcomes,
    predictors,
    covariates: list = [],
    robust_cov: str = "HC3",
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
):
    """
    Run OLS for every (struct, predictor).
    Returns (results_by_struct, results_by_predictor)
    - results_by_struct: dict struct -> DataFrame indexed by predictor
    - results_by_predictor: dict predictor -> DataFrame indexed by struct
    Each DataFrame columns: coef, pval, se, llci, ulci, ci, R2, p_fdr, coef_sig
    """
    if covariates is None:
        covariates = []
    outcomes = list(outcomes)
    predictors = list(predictors)
    # container: per-struct dataframes
    results_by_struct = {}
    
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

    for struct in outcomes:
        rows = []
        for pred in predictors:
            exog = [pred] + covariates
            formula = f"{struct} ~ {" + ".join(exog)}"
            try:
                res = sm.OLS.from_formula(formula, data=model_data).fit()
                if robust_cov:
                    rres = res.get_robustcov_results(cov_type=robust_cov)
                else:
                    rres = res

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
                }
            )
        df_struct = pd.DataFrame(rows).set_index("predictor")
        # FDR across predictors for this struct
        pvals = df_struct["pval"].fillna(1.0).values 
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        df_struct.insert(2, "p_fdr", p_fdr_vals)
        df_struct["coef_sig"] = df_struct["coef"].where(df_struct["p_fdr"] < fdr_alpha, 0.0)
        results_by_struct[struct] = df_struct

    # build results_by_predictor for compatibility
    results_by_predictor = {}
    cols = next(iter(results_by_struct.values())).columns
    for pred in predictors:
        rows = []
        for struct in outcomes:
            row = results_by_struct[struct].loc[pred].to_dict()
            row["struct"] = struct
            rows.append(row)
        df_pred = pd.DataFrame(rows).set_index("struct")[cols]
        results_by_predictor[pred] = df_pred

    return results_by_struct, results_by_predictor