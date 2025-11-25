from collections import defaultdict
from typing import Optional, Union
from warnings import simplefilter

import pandas as pd
from IPython.display import Markdown, display
from statsmodels.base.wrapper import ResultsWrapper
from statsmodels.stats.multitest import multipletests

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
from pandas.api.types import is_numeric_dtype

from statsmodels.stats.outliers_influence import variance_inflation_factor

import helpers
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from collections.abc import Iterable
import utils
import pingouin as pg
from scipy import stats


from my_namespace import presentation_cols

colors = utils.get_colors()


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
    model_data: pd.DataFrame,
    dependent_var: str,
    independent_vars: list[str],
    regression_model: str = "OLS",
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
    if regression_model == "OLS":
        model = sm.OLS.from_formula(formula, data=model_data).fit()
        return model.resid
    elif regression_model == "GLM":
        family = sm.families.Poisson()
        model = sm.GLM.from_formula(formula, data=model_data, family=family).fit()
        return model.resid_pearson
    else:
        raise Exception


format_opts_ref = {
    "coef": "{:.4f}",
    "se": "{:.4f}",
    "pval": "{:.2}",
    "p_fdr": "{:.2}",
    "R2": "{:.2}",
}


def format_df(df: pd.DataFrame, format_dict):
    """Apply Styler-like formatting but output to markdown"""
    df_copy = df.copy()
    for col, fmt in format_dict.items():
        if col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].map(lambda x: fmt.format(x))
            except TypeError:
                df_copy.drop(columns=[col], inplace=True)
    return df_copy


def present_model(
    model: pd.DataFrame,
    cols: list = None,
    inds: list = None,
    exclude_inds: list = None,
    rename_index: dict = None,
    rename_cols: dict = None,
    format_opts: dict = format_opts_ref,
):
    # cols = ["coef", ("p_fdr", "pval"), "se", "ci", "R2"]
    if cols is None:
        cols = model.columns
    if inds is None:
        inds = []
    if exclude_inds is None:
        exclude_inds = []
    if rename_index is None:
        rename_index = {k: k for k in model.index}
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
        present_index = model.index.to_list()

    for ind in exclude_inds:
        try:
            present_index.remove(ind)
        except ValueError:
            pass

    for col in present_cols:
        if col not in format_opts and is_numeric_dtype(model[col]):
            if "pval" in col or "fdr" in col:
                format_opts[col] = "{:.2}"
            else:
                format_opts[col] = "{:.4f}"
    model = format_df(model.loc[present_index, present_cols], format_opts)

    return model


def plot_moderation(
    plot_data,
    y_name,
    x_name,
    w_name,
    covariates=None,
    xlab_name=None,
    ylab_name=None,
    wlab_name=None,
):
    if xlab_name is None:
        xlab_name = x_name
    if ylab_name is None:
        ylab_name = y_name
    if wlab_name is None:
        wlab_name = w_name

    if covariates is not None:
        plus_covariates = f"+ {' + '.join(covariates)}"
    else:
        plus_covariates = ""

    xcent_name = f"{x_name}_cent"
    wcent_name = f"{w_name}_cent"
    plot_data[xcent_name] = plot_data[x_name] - plot_data[x_name].mean()
    plot_data[wcent_name] = plot_data[w_name] - plot_data[w_name].mean()

    formula = f"{y_name} ~ {wcent_name}*{xcent_name} {plus_covariates}"
    res = sm.OLS.from_formula(formula, data=plot_data).fit()

    x_rng, y_lvls = helpers.moderation_y(plot_data, res, xcent_name, wcent_name)
    # fix x_rng since the moderation_y took the centered version
    x_rng = np.linspace(plot_data[x_name].min(), plot_data[x_name].max(), 100)
    # x_rng = np.linspace(0, 20, 100)

    # helpers.plot_moderation(model_data['dzdur'], model_data['EDSS'], x_rng, y_lvls)
    # plt.scatter(model_data[x_name], model_data[y_name], s=8, color=viridis(cmap))
    plt.scatter(plot_data[x_name], plot_data[y_name], s=8)

    # m-sd line
    plt.plot(
        x_rng, y_lvls[0][0], label="m-sd", linestyle="--", color=colors["dark blue1"]
    )
    # plt.fill_between(x_rng, y_lvls[0][1], y_lvls[0][2], color=colors['light blue1'], alpha=0.1)

    plt.plot(
        x_rng, y_lvls[1][0], label=f"m ({wlab_name})", linestyle="-", color="black"
    )
    plt.fill_between(x_rng, y_lvls[1][1], y_lvls[1][2], color="grey", alpha=0.2)

    plt.plot(
        x_rng, y_lvls[2][0], label="m+sd", linestyle="--", color=colors["dark red1"]
    )
    # plt.fill_between(x_rng, y_lvls[2][1], y_lvls[2][2], color=colors['light red1'], alpha=0.1)

    plt.legend()
    plt.xlabel(xlab_name)
    plt.ylabel(ylab_name)
    plt.show()
    
    
def check_vif(data, variables):
    X = data[variables]
    X = X.dropna()
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    if any(vif_data["VIF"] > 10):
        print(f"WARNING: SEVERE VIF (>10)\n{", ".join(variables)}")
        return "severe", vif_data
    if any(vif_data["VIF"] > 5):
        print(f"WARNING: Moderate VIF (>5)\n{", ".join(variables)}")
        return "moderate", vif_data
    else:
        return "good", vif_data


def run_regressions(
    model_data: pd.DataFrame,
    outcomes: Union[str, Iterable[str]],
    predictors: Iterable[str],
    covariates: Optional[Iterable[str]] = None,
    robust_cov: str = "HC3",
    regression_model: str = "OLS",
    family: Optional[str] = None,
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
    to_check_vif: bool = True,
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    dict[tuple[str, str], ResultsWrapper],
]:
    """
    Run regressions for all combinations of outcomes and predictors.

    Fits separate regression models for each (outcome, predictor) pair, controlling
    for specified covariates. Applies FDR correction across multiple comparisons
    and returns results organized by outcome and by predictor.

    Parameters
    ----------
    model_data : pd.DataFrame
        DataFrame containing all variables (outcomes, predictors, covariates).
    outcomes : str or list of str
        Outcome variable(s) to model. If string, treated as single outcome.
    predictors : list of str or set of str
        Predictor variables of interest. Each is tested separately.
    covariates : list of str, default=[]
        Control variables included in all models.
    robust_cov : str, default="HC3"
        Covariance estimator type. Valid values:
        - "HC0", "HC1", "HC2", "HC3": Heteroscedasticity-robust standard errors
        - "nonrobust": Standard OLS covariance (homoscedasticity assumed)
        Ignored when regression_model is not "OLS".
    regression_model : str, default="OLS"
        Type of regression model to fit. Valid values:
        - "OLS": Ordinary least squares
        - "GLM": Generalized linear model (requires `family` parameter)
        - "Logit": Logistic regression
    family : sm.families.Family, optional
        GLM family object (e.g., sm.families.Poisson()). Required when
        regression_model="GLM", ignored otherwise.
    fdr_method : str, default="fdr_bh"
        Method for FDR correction (passed to statsmodels.multipletests).
    fdr_alpha : float, default=0.05
        Significance threshold for FDR correction.

    Returns
    -------
    results_by_outcome : dict of {str: pd.DataFrame}
        Results organized by outcome. Keys are outcome names, values are
        DataFrames indexed by predictor with columns:
        - coef: regression coefficient
        - pval: uncorrected p-value
        - p_fdr: FDR-corrected p-value
        - se: standard error
        - llci, ulci: confidence interval bounds
        - ci: formatted confidence interval string
        - R2: adjusted R² (OLS) or pseudo-R² (GLM), None for Logit
        - coef_sig: coefficient if p_fdr < fdr_alpha, else 0
        - formula: regression formula used
    results_by_predictor : dict of {str: pd.DataFrame}
        Results organized by predictor. Keys are predictor names, values are
        DataFrames indexed by outcome with same columns as above.
    models : dict of {tuple[str, str]: ResultsWrapper}
        Fitted model objects indexed by (outcome, predictor) tuple.

    Raises
    ------
    Exception
        Re-raises any exception from model fitting with context about which
        outcome and predictor caused the error.

    Notes
    -----
    - FDR correction is applied separately within each outcome (across predictors)
      and within each predictor (across outcomes).
    - For GLM models, family defaults to Poisson if not specified.
    - Robust covariance is automatically disabled for non-OLS models.

    Examples
    --------
    >>> results_out, results_pred, models = run_regressions(
    ...     model_data=df,
    ...     outcomes=['disability_score', 'cognitive_score'],
    ...     predictors=['choroid_plexus_vol', 'ventricle_vol'],
    ...     covariates=['age', 'sex'],
    ...     robust_cov='HC3'
    ... )
    >>> results_out['disability_score']  # coefficients for all predictors
    """

    if covariates is None:
        covariates = []
    if isinstance(predictors, set):
        predictors = list(predictors)

    single_outcome = False
    if isinstance(outcomes, str):
        outcomes = [outcomes]
        single_outcome = True

    # container: per-outcome dataframes
    results_by_outcome = {}
    models = defaultdict(dict)
    for outcome in outcomes:
        rows = []
        for pred in predictors:
            exog = [pred] + covariates
            
            if to_check_vif:
                message, vif = check_vif(model_data, exog+[outcome])
                if message == "severe" or message == "moderate":
                    # print(f"Outcome: {outcome}\nExog: {", ".join(exog)}")
                    pass
            
            formula = f"{outcome} ~ {' + '.join(exog)}"
            try:
                if regression_model == "OLS":
                    rres = sm.OLS.from_formula(formula, data=model_data).fit(
                        cov_type=robust_cov
                    )
                    r2 = rres.rsquared_adj
                elif regression_model == "GLM":
                    if family is None:
                        family = sm.families.Poisson()
                    rres = smf.glm(formula, data=model_data, family=family).fit(
                        cov_type=robust_cov
                    )
                    r2 = rres.pseudo_rsquared()
                elif regression_model == "Logit":
                    rres = smf.Logit(formula, data=model_data).fit(
                        cov_type=robust_cov, disp=0
                    )
                    r2 = None

                # * can switch to frozenset if it becomes really helpful to index without worrying about order
                models[(outcome, pred)] = rres
                coef = rres.params[pred]
                pval = rres.pvalues[pred]
                se = rres.bse[pred]

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

            except Exception as e:
                print(f"Error occurred while processing {pred} for {outcome}: {e}")
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
        results_by_outcome[outcome] = df_struct

    # build results_by_predictor for compatibility
    results_by_predictor = {}
    cols = next(iter(results_by_outcome.values())).columns
    for pred in predictors:
        rows = []
        for outcome in outcomes:
            row = results_by_outcome[outcome].loc[pred].to_dict()
            row["outcome"] = outcome
            rows.append(row)
        df_pred = pd.DataFrame(rows).set_index("outcome")[cols]
        pvals = df_pred["pval"].fillna(1.0).values
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        df_pred["p_fdr"] = p_fdr_vals
        df_pred["coef_sig"] = df_struct["coef"].where(
            df_struct["p_fdr"] < fdr_alpha, 0.0
        )
        results_by_predictor[pred] = df_pred

    if single_outcome:
        results_by_outcome = results_by_outcome[outcomes[0]]

    return results_by_outcome, results_by_predictor, models


def run_regressions_multimodel(
    model_data: pd.DataFrame,
    outcome: str,
    exog_list: list[list[str]],
    model_names: Optional[list[str]] = None,
    covariates: Optional[list[str]] = None,
    robust_cov: str = "HC3",
    regression_model: str = "OLS",
    family: Optional[sm.families.Family] = None,
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
    to_check_vif: bool = True,
) -> tuple[dict[str, pd.DataFrame], dict[str, ResultsWrapper], dict[str, str]]:
    """
    Run multiple regression models for a single outcome with different predictor sets.

    Fits separate regression models for one outcome variable, each using a different
    set of predictors. Useful for comparing nested models or testing different
    predictor combinations while controlling for the same covariates.

    Parameters
    ----------
    model_data : pd.DataFrame
        DataFrame containing all variables (outcome, predictors, covariates).
    outcome : str
        Outcome variable to model across all specifications.
    exog_list : list of list of str
        List of predictor sets. Each inner list contains variable names for one model.
        Example: [['age'], ['age', 'sex'], ['age', 'sex', 'education']]
    model_names : list of str, optional
        Names for each model specification. If None, uses integer indices (0, 1, 2, ...).
    covariates : list of str, optional
        Control variables included in ALL models (in addition to each exog set).
    robust_cov : str, default="HC3"
        Covariance estimator type. Valid values:
        - "HC0", "HC1", "HC2", "HC3": Heteroscedasticity-robust standard errors
        - "nonrobust": Standard OLS covariance (homoscedasticity assumed)
        Ignored when regression_model is not "OLS".
    regression_model : str, default="OLS"
        Type of regression model to fit. Valid values:
        - "OLS": Ordinary least squares
        - "GLM": Generalized linear model (requires `family` parameter)
        - "Logit": Logistic regression
    family : sm.families.Family, optional
        GLM family object (e.g., sm.families.Poisson()). Required when
        regression_model="GLM", ignored otherwise.
    fdr_method : str, default="fdr_bh"
        Method for FDR correction (passed to statsmodels.multipletests).
    fdr_alpha : float, default=0.05
        Significance threshold for FDR correction.

    Returns
    -------
    results : dict of {str: pd.DataFrame}
        Regression results indexed by model name. Each DataFrame is indexed by
        variable names (predictors + covariates + intercept) with columns:
        - coef: regression coefficient
        - pval: uncorrected p-value
        - se: standard error
        - llci, ulci: confidence interval bounds
        - ci: formatted confidence interval string
        - R2: adjusted R² (OLS) or pseudo-R² (GLM), None for Logit
    models : dict of {str: ResultsWrapper}
        Fitted model objects indexed by model name.
    formulas : dict of {str: str}
        Regression formulas indexed by model name.

    Raises
    ------
    Exception
        Re-raises any exception from model fitting with context about which
        model specification caused the error.

    Notes
    -----
    - All models use the same outcome variable but different predictor combinations.
    - Covariates are automatically added to every model specification.
    - Robust covariance is automatically disabled for non-OLS models.

    Examples
    --------
    >>> # Test nested models with increasing complexity
    >>> results, models, formulas = run_regressions_multimodel(
    ...     model_data=df,
    ...     outcome='disability_score',
    ...     exog_list=[
    ...         ['choroid_plexus_vol'],
    ...         ['choroid_plexus_vol', 'ventricle_vol'],
    ...         ['choroid_plexus_vol', 'ventricle_vol', 'thalamus_vol']
    ...     ],
    ...     model_names=['Model1', 'Model2', 'Model3'],
    ...     covariates=['age', 'sex']
    ... )
    >>> results['Model1']  # coefficients for simplest model
    """
    if model_names is None:
        model_names = [str(i) for i, _ in enumerate(exog_list)]
    if covariates is None:
        covariates = []
    if regression_model != "OLS":
        robust_cov = False

    results = {}
    models = {}
    formulas = {}
    for exog, model_name in zip(exog_list, model_names):
        independent_vars = exog + covariates
        
        if to_check_vif:
            message, vif = check_vif(model_data, independent_vars+[outcome])
            if message == "severe" or message == "moderate":
                # print(f"Outcome: {outcome}\nExog: {", ".join(independent_vars)}")
                pass
            
        formula = f"{outcome} ~ {' + '.join(independent_vars)}"
        try:
            if regression_model == "OLS":
                rres = sm.OLS.from_formula(formula, data=model_data).fit(
                    cov_type=robust_cov
                )
                r2 = rres.rsquared_adj
            elif regression_model == "GLM":
                if family is None:
                    family = sm.families.Poisson()
                rres = smf.glm(formula, data=model_data, family=family).fit(
                    cov_type=robust_cov
                )
                r2 = rres.pseudo_rsquared()
            elif regression_model == "Logit":
                rres = smf.logit(formula, data=model_data).fit(disp=0)
                r2 = None
            else:
                raise Exception("Invalid input for regression_model")

            models[model_name] = rres
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

            exog_names = list(rres.model.exog_names)
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
                "R2": r2,
            },
            index=exog_names,
        )
        pvals = res_df["pval"].fillna(1.0).values
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        res_df.insert(2, "p_fdr", p_fdr_vals)
        results[model_name] = res_df
        formulas[model_name] = formula

    return results, models, formulas


def run_regressions_from_formulas(
    model_data: pd.DataFrame,
    formula_list: list[str],
    model_names: list[str] | None = None,
    covariates: list[str] | None = None,
    robust_cov: str = "HC3",
    regression_model: str = "OLS",
    family: Optional[sm.families.Family] = None,
    to_check_vif: bool = True,
) -> tuple[dict[str, pd.DataFrame], dict[str, ResultsWrapper], dict[str, str]]:
    """
    Run regression models from R-style formula specifications.

    Fits multiple regression models using patsy/R-style formulas. Provides maximum
    flexibility for model specification including transformations, interactions,
    and categorical encoding.

    Parameters
    ----------
    model_data : pd.DataFrame
        DataFrame containing all variables referenced in formulas.
    formula_list : list of str
        List of R-style regression formulas (e.g., 'y ~ x1 + x2 + x1:x2').
        Each formula represents one model specification.
    model_names : list of str, optional
        Names for each model. If None, uses integer indices (0, 1, 2, ...).
    robust_cov : str, default="HC3"
        Covariance estimator type. Valid values:
        - "HC0", "HC1", "HC2", "HC3": Heteroscedasticity-robust standard errors
        - "nonrobust": Standard OLS covariance (homoscedasticity assumed)
        Ignored when regression_model is not "OLS".
    regression_model : str, default="OLS"
        Type of regression model to fit. Valid values:
        - "OLS": Ordinary least squares
        - "GLM": Generalized linear model (requires `family` parameter)
        - "Logit": Logistic regression
    family : sm.families.Family, optional
        GLM family object (e.g., sm.families.Poisson()). Required when
        regression_model="GLM", ignored otherwise.

    Returns
    -------
    results : dict of {str: pd.DataFrame}
        Regression results indexed by model name. Each DataFrame is indexed by
        variable/term names with columns:
        - coef: regression coefficient
        - pval: uncorrected p-value
        - se: standard error
        - llci, ulci: confidence interval bounds
        - ci: formatted confidence interval string
        - R2: adjusted R² (OLS) or pseudo-R² (GLM), None for Logit
    models : dict of {str: ResultsWrapper}
        Fitted model objects indexed by model name.
    formulas : dict of {str: str}
        Copy of input formulas indexed by model name.

    Raises
    ------
    Exception
        Re-raises any exception from model fitting with context about which
        formula caused the error.

    Notes
    -----
    - Formulas support patsy syntax including:
      * Transformations: 'y ~ np.log(x1) + x2**2'
      * Interactions: 'y ~ x1 + x2 + x1:x2' or 'y ~ x1 * x2'
      * Categorical encoding: 'y ~ C(group) + x1'
    - Robust covariance is automatically disabled for non-OLS models.

    Examples
    --------
    >>> # Compare models with different interaction structures
    >>> formulas = [
    ...     'disability ~ choroid_plexus_vol + age + sex',
    ...     'disability ~ choroid_plexus_vol * ventricle_vol + age + sex',
    ...     'disability ~ np.log(choroid_plexus_vol) + ventricle_vol + age + sex'
    ... ]
    >>> results, models, _ = run_regressions_from_formulas(
    ...     model_data=df,
    ...     formula_list=formulas,
    ...     model_names=['Main_Effects', 'With_Interaction', 'Log_Transform']
    ... )
    >>> results['With_Interaction']  # coefficients including interaction term
    """
    if model_names is None:
        model_names = [str(i) for i, _ in enumerate(formula_list)]
    if covariates is None:
        covariates = []

    models = {}
    results = {}
    formulas = {}
    for formula, model_name in zip(formula_list, model_names):
        try:
            formula = " + ".join([formula] + (covariates))
            
            if to_check_vif:
                formula_split = formula.split(" + ")
                variables = formula_split[1:] + formula_split[0].split(" ~ ")
                message, vif = check_vif(model_data, variables)
                if message == "severe" or message == "moderate":
                    # print(formula)
                    pass
                
            if regression_model == "OLS":
                rres = sm.OLS.from_formula(formula, data=model_data).fit(
                    cov_type=robust_cov
                )
                r2 = rres.rsquared_adj
            elif regression_model == "GLM":
                if family is None:
                    family = sm.families.Poisson()
                rres = smf.glm(formula, data=model_data, family=family).fit(
                    cov_type=robust_cov
                )
                r2 = rres.pseudo_rsquared()
            elif regression_model == "Logit":
                rres = smf.Logit(formula, data=model_data).fit(
                    cov_type=robust_cov, disp=0
                )
                r2 = None

            models[model_name] = rres
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

            exog_names = list(rres.model.exog_names)
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
                "R2": r2,
            },
            index=exog_names,
        )
        results[model_name] = res_df
        formulas[model_name] = formula

    return results, models, formulas


def run_partial_regressions(
    model_data: pd.DataFrame,
    outcomes: str | list[str],
    predictors: list[str] | set[str],
    covariates: list[str] = None,
    corr_type: Optional[str] = None,
    robust_cov: str = "HC3",
    regression_models: str | list[str] = "OLS",
    family: Optional[sm.families.Family] = None,
    fdr_method: str = "fdr_bh",
    fdr_alpha: float = 0.05,
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    dict[tuple[str, str], ResultsWrapper],
]:
    """
    Run regressions for all combinations of outcomes and predictors.

    Fits separate regression models for each (outcome, predictor) pair, controlling
    for specified covariates. Applies FDR correction across multiple comparisons
    and returns results organized by outcome and by predictor.

    Parameters
    ----------
    model_data : pd.DataFrame
        DataFrame containing all variables (outcomes, predictors, covariates).
    outcomes : str or list of str
        Outcome variable(s) to model. If string, treated as single outcome.
    predictors : list of str or set of str
        Predictor variables of interest. Each is tested separately.
    covariates : list of str, default=[]
        Control variables included in all models.
    robust_cov : str, default="HC3"
        Covariance estimator type. Valid values:
        - "HC0", "HC1", "HC2", "HC3": Heteroscedasticity-robust standard errors
        - "nonrobust": Standard OLS covariance (homoscedasticity assumed)
        Ignored when regression_model is not "OLS".
    regression_model : str, default="OLS"
        Type of regression model to fit. Valid values:
        - "OLS": Ordinary least squares
        - "GLM": Generalized linear model (requires `family` parameter)
        - "Logit": Logistic regression
    family : sm.families.Family, optional
        GLM family object (e.g., sm.families.Poisson()). Required when
        regression_model="GLM", ignored otherwise.
    fdr_method : str, default="fdr_bh"
        Method for FDR correction (passed to statsmodels.multipletests).
    fdr_alpha : float, default=0.05
        Significance threshold for FDR correction.

    Returns
    -------
    results_by_outcome : dict of {str: pd.DataFrame}
        Results organized by outcome. Keys are outcome names, values are
        DataFrames indexed by predictor with columns:
        - coef: regression coefficient
        - pval: uncorrected p-value
        - p_fdr: FDR-corrected p-value
        - se: standard error
        - llci, ulci: confidence interval bounds
        - ci: formatted confidence interval string
        - R2: adjusted R² (OLS) or pseudo-R² (GLM), None for Logit
        - coef_sig: coefficient if p_fdr < fdr_alpha, else 0
        - formula: regression formula used
    results_by_predictor : dict of {str: pd.DataFrame}
        Results organized by predictor. Keys are predictor names, values are
        DataFrames indexed by outcome with same columns as above.
    models : dict of {tuple[str, str]: ResultsWrapper}
        Fitted model objects indexed by (outcome, predictor) tuple.

    Raises
    ------
    Exception
        Re-raises any exception from model fitting with context about which
        outcome and predictor caused the error.

    Notes
    -----
    - FDR correction is applied separately within each outcome (across predictors)
      and within each predictor (across outcomes).
    - For GLM models, family defaults to Poisson if not specified.
    - Robust covariance is automatically disabled for non-OLS models.

    Examples
    --------
    >>> results_out, results_pred, models = run_regressions(
    ...     model_data=df,
    ...     outcomes=['disability_score', 'cognitive_score'],
    ...     predictors=['choroid_plexus_vol', 'ventricle_vol'],
    ...     covariates=['age', 'sex'],
    ...     robust_cov='HC3'
    ... )
    >>> results_out['disability_score']  # coefficients for all predictors
    """

    if covariates is None:
        covariates = []
    if isinstance(predictors, set):
        predictors = list(predictors)

    single_outcome = False
    if isinstance(outcomes, str):
        outcomes = [outcomes]
        single_outcome = True

    if isinstance(regression_models, str):
        regression_models = {k: regression_models for k in outcomes + predictors}

    resid_data = model_data.copy()
    for outcome in outcomes:
        resid_data[outcome] = residualize_vars(
            model_data, outcome, covariates, regression_model=regression_models[outcome]
        )
    for predictor in predictors:
        resid_data[predictor] = residualize_vars(
            model_data,
            predictor,
            covariates,
            regression_model=regression_models[predictor],
        )
    # container: per-outcome dataframes
    results_by_outcome = {}
    models = defaultdict(dict)
    for outcome in outcomes:
        rows = []
        for predictor in predictors:
            exog = [predictor] + covariates
            formula = f"{outcome} ~ {' + '.join(exog)}"
            try:
                if corr_type is None:
                    rres = sm.OLS.from_formula(
                        f"{outcome} ~ {predictor}", data=utils.zscore(resid_data)
                    ).fit(cov_type=robust_cov)
                    r2 = rres.rsquared_adj
                    coef = rres.params[predictor]
                    pval = rres.pvalues[predictor]
                    se = rres.bse[predictor]

                    # confidence interval: conf_int() returns DataFrame when names available
                    ci_df = rres.conf_int()
                    llci, ulci = (
                        float(ci_df.loc[predictor, 0]),
                        float(ci_df.loc[predictor, 1]),
                    )
                    ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""

                else:
                    rres = pg.corr(
                        resid_data[predictor],
                        resid_data[outcome],
                        method=corr_type,
                        alternative="two-sided",
                    )
                    coef = rres.loc[corr_type, "r"]
                    pval = rres.loc[corr_type, "p-val"]
                    ci = rres.loc[corr_type, "CI95%"]
                    llci, ulci = float(ci[0]), float(ci[1])
                    ci_str = f"[{llci:.3}, {ulci:.3}]" if not np.isnan(llci) else ""
                    se = None
                    r2 = None
                # * can switch to frozenset if it becomes really helpful to index without worrying about order
                models[(outcome, predictor)] = rres

            except Exception as e:
                print(f"Error occurred while processing {predictor} for {outcome}: {e}")
                coef = pval = se = llci = ulci = np.nan
                ci_str = ""
                r2 = np.nan
                raise e
            rows.append(
                {
                    "predictor": predictor,
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
        results_by_outcome[outcome] = df_struct

    # build results_by_predictor for compatibility
    results_by_predictor = {}
    cols = next(iter(results_by_outcome.values())).columns
    for pred in predictors:
        rows = []
        for outcome in outcomes:
            row = results_by_outcome[outcome].loc[pred].to_dict()
            row["outcome"] = outcome
            rows.append(row)
        df_pred = pd.DataFrame(rows).set_index("outcome")[cols]
        pvals = df_pred["pval"].fillna(1.0).values
        _, p_fdr_vals, _, _ = multipletests(pvals, alpha=fdr_alpha, method=fdr_method)
        df_pred["p_fdr"] = p_fdr_vals
        df_pred["coef_sig"] = df_struct["coef"].where(
            df_struct["p_fdr"] < fdr_alpha, 0.0
        )
        results_by_predictor[pred] = df_pred

    if single_outcome:
        results_by_outcome = results_by_outcome[outcomes[0]]

    return results_by_outcome, results_by_predictor, models


def compare_models(base, full, base_model_name=None, full_model_name=None):
    if base_model_name is None:
        base_model_name = "+".join(
            [
                var
                for var in base.model.exog_names
                if var
                not in ["Intercept", "Female", "Female[T.1]", "age", "tiv", "TIV"]
            ]
        )
    if full_model_name is None:
        full_model_name = "+".join(
            [
                var
                for var in full.model.exog_names
                if var
                not in ["Intercept", "Female", "Female[T.1]", "age", "tiv", "TIV"]
            ]
        )

    model_comparisons = pd.Series(
        index=[
            "base model",
            "full model",
            "ΔR",
            "F-statistic",
            "F-test pval",
            "LR",
            "LR pval",
            "df",
        ]
    )

    del_R = full.rsquared_adj - base.rsquared_adj
    del_df = full.df_model - base.df_model

    model_comparisons[["base model", "full model", "ΔR"]] = [
        base_model_name,
        full_model_name,
        del_R,
    ]
    model_comparisons[["F-statistic", "F-test pval", "df"]] = full.compare_f_test(base)
    model_comparisons["LR"] = 2 * (full.llf - base.llf)
    model_comparisons["LR pval"] = stats.chi2.sf(model_comparisons["LR"], df=del_df)

    return model_comparisons


def display_results(
    result,
    formula=None,
    outcome=None,
    predictor=None,
    covariates=None,
    heading=None,
    exclude_inds=None,
    same_R2=False,
    presentation_cols=presentation_cols,
):
    if exclude_inds is None:
        exclude_inds = ["Intercept", "age", "Female[T.1]", "tiv"]
    if formula is None:
        try:
            formula = formula_string(outcome, predictor, covariates)
        except TypeError:
            formula = None
    display_order = result["coef"].sort_values(ascending=False).index

    display_text = ""
    if heading is not None:
        display_text += heading + "\n\n"
        display(Markdown(heading))
    if formula is not None:
        formula_text = f"```R\n{formula}\n```"
        display_text += formula_text + "\n\n"
        display(Markdown(formula_text))
    model_to_present = present_model(
        result, cols=presentation_cols, inds=display_order, exclude_inds=exclude_inds
    )
    if same_R2:
        model_to_present.loc[model_to_present.index[1:], "R2"] = "____"

    table_text = model_to_present.to_markdown()
    display_text += table_text
    display(Markdown(table_text))

    return display_text


def compute_se_diff(se1, n1, se2, n2):
    return np.sqrt((se1**2/n1) + (se2**2/n2))

def scatter_hist(
    x, y, ax, ax_histx, ax_histy, nbins=10, light_color=None, dark_color=None
):
    if light_color is None:
        light_color = "#1f77b4"
    if dark_color is None:
        dark_color = "#1f77b4"

    # make axes look nice
    ax_histx.set_axis_off()
    ax_histy.set_axis_off()
    ax.xaxis.set_ticks_position("both")
    ax.yaxis.set_ticks_position("both")

    # the scatter plot:
    ax.scatter(x, y, color=dark_color)
    ylim = ax.get_ylim()

    # the histograms
    xbins = np.linspace(np.min(x), np.max(x), nbins)
    ybins = np.linspace(np.min(y), np.max(y), nbins)
    ax_histx.hist(x, bins=xbins, color="gray", density=True)
    ax_histy.hist(
        y, bins=ybins, orientation="horizontal", color=light_color, density=True
    )

    # kde to plot on histograms
    densityx = stats.gaussian_kde(x.dropna())
    densityy = stats.gaussian_kde(y.dropna())
    xx = np.linspace(np.min(x), np.max(x), 50)
    xy = np.linspace(np.min(y), np.max(y), 50)
    ax_histx.plot(xx, densityx(xx), color="black")
    ax_histy.plot(densityy(xy), xy, color=dark_color)
    
    ax_histy.set_ylim(ylim)


def plot_regression(
    data, predictor, outcome, covariates, xlabel=None, ylabel=None, title=None,
    color="blue1", light_color=None, dark_color=None
):
    plus_covariates = ""
    if len(covariates) > 0:
        plus_covariates = f"+ {' + '.join(covariates)}"
    if xlabel is None:
        xlabel = predictor
    if ylabel is None:
        ylabel = outcome
    if title is None:
        title = f"{outcome} vs {predictor}"
    
    if light_color is None:
        light_color = f"light {color}"
    if dark_color is None:
        dark_color = f"dark {color}"
    light_color = colors[light_color]  
    dark_color = colors[dark_color]

    formula = f"{outcome} ~ {predictor} {plus_covariates}"
    res = sm.OLS.from_formula(formula, data=data).fit()
    
    
    x, y_pred, y_lims = helpers.get_regression_y(data, res, predictor, outcome)

    fig, axs = plt.subplot_mosaic(
        [['histx', '.'], ['scatter', 'histy']],
        figsize=(8, 6),
        width_ratios=(4, 1),
        height_ratios=(1, 4),
        layout='constrained'
    )
    axs['scatter'].plot(x, y_pred, color="black")
    axs['scatter'].fill_between(
        x, y_lims[0], y_lims[1], alpha=0.4, color=light_color
    )
    scatter_hist(
        data[predictor],
        data[outcome],
        axs['scatter'],
        axs['histx'],
        axs['histy'],
        light_color=light_color,
        dark_color=dark_color,
    )

    axs['scatter'].set_ylabel(ylabel)
    axs['scatter'].set_xlabel(xlabel)
    fig.suptitle(title)
    return fig, axs