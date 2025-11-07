import pandas as pd
from mri_data import file_manager as fm
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from pathlib import Path
import re
import statsmodels.api as sm
import numpy as np
from scipy import stats
import datetime
from datetime import timedelta
from datetime import datetime
import pyperclip
import textwrap
import sys
from io import StringIO



pd.options.mode.copy_on_write = True

msmri_home = Path("/home/srs-9/Projects/ms_mri")
msmri_datadir = msmri_home / "data"
monai_analysis_dir = msmri_home / "monai_analysis"

analysis_folders = {
    "t1": "choroid_pineal_pituitary_T1-1",
    "flair": "choroid_pineal_pituitary_FLAIR-1",
}

keep_cols = [
    "subject",
    "age",
    "sex",
    "ms_type",
    "dzdur",
    "extracted_EDSS",
    "MSSS",
    "gMSSS",
    "ARMSS",
    "DMT_score",
    "DMT_hx_all",
    "TER",
    "DMF",
    "NAT",
    "INF",
    "flair_contrast",
    "thalamus",
    "brain",
    "white",
    "grey",
    "cortical_thickness",
    "lesion_count",
    "lesion_vol_cubic",
    "PRL",
    "tiv",
    "choroid_volume",
    "pineal_volume",
    "pituitary_volume",
]


numeric_vars = [
    "age",
    "dzdur",
    "EDSS",
    "EDSS_sqrt",
    "MSSS",
    "MSSS_sqrt",
    "gMSSS",
    "gMSSS_sqrt",
    "ARMSS",
    "ARMSS_sqrt",
    "DMT_score",
    "DMT_hx_all",
    "TER",
    "DMF",
    "NAT",
    "INF",
    "thalamus",
    "brain",
    "white",
    "grey",
    "cortical_thickness",
    "lesion_count",
    "lesion_vol",
    "t2lv",
    "t2lv_logtrans",
    "PRL",
    "tiv",
    "choroid_volume",
    "pineal_volume",
    "pituitary_volume",
]

vars_to_center = [
    "edss_sqrt",
    "lesion_vol_logtrans",
    "lesion_vol_cubic",
    "dzdur",
    "choroid_volume",
]


def quick_regression(y, x, data, covariates=None):
    if covariates is None:
        covariates = ["age", "Female", "tiv"]
    exog = [x] + covariates
    formula = f"{y} ~ {' + '.join(exog)}"
    res = sm.OLS.from_formula(formula, data=data).fit()
    return res, formula


def residualize_structs(
    model_data: pd.DataFrame, dependent_var: str, independent_vars: list[str]
):
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


def load_df():
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

    tiv = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/data/tiv_data.csv", index_col="subid"
    )

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
            sdmt["SDMT"],
        ]
    )
    df["SDMT"] = pd.to_numeric(df["SDMT"], errors="coerce")
    rename_columns = {
        "ventricle_volume": "LV",
        "choroid_volume": "CP",
        "peripheral": "periCSF",
        "all": "allCSF",
        "third_ventricle": "thirdV",
        "fourth_ventricle": "fourthV",
        "aseg_csf": "asegCSF",
        "third_ventricle_width": "thirdV_width",
    }
    df.rename(columns=rename_columns, inplace=True)

    return df


def load_hipsthomas(data_dir, side=None):
    if side is not None:
        filename = f"hipsthomas_{side}_vols.csv"
    else:
        filename = "hipsthomas_vols.csv"

    df_thomas = pd.read_csv(data_dir / filename, index_col="subid")

    new_colnames = {}
    for col in df_thomas.columns:
        new_col = re.sub(r"(\d+)-([\w-]+)", r"\2_\1", col)
        new_col = re.sub("-", "_", new_col)
        new_colnames[col] = new_col

    df_thomas = df_thomas.rename(columns=new_colnames)

    nuclei_groupings = {
        "anterior": ["AV_2"],
        "ventral": ["VA_4", "VLa_5", "VLP_6", "VPL_7"],
        "posterior": ["Pul_8", "LGN_9", "MGN_10"],
        "medial": ["MD_Pf_12", "CM_11"],
    }

    def combine_nuclei(df, groupings):
        df2 = pd.DataFrame()
        for group, nuclei in groupings.items():
            df2[group] = sum([df[nucleus] for nucleus in nuclei])
        return df2

    df_thomas = df_thomas.join(combine_nuclei(df_thomas, nuclei_groupings))

    return df_thomas


# maybe print a log of what what composited 
def composite_vars(df):
    df["CCF0"] = df["LV"] / df["allCSF"]
    df["CCF"] = df["LV"] / (df["LV"] + df["periCSF"])
    df["CCR"] = df["LV"] / df["periCSF"]
    df["periCSF_ratio"] = df["periCSF"] / df["LV"]
    df["periCSF_frac"] = df["periCSF"] / df["allCSF"]
    df["thirdV_expansion"] = df['thirdV_width'] / df['thirdV']
    return df


def normalize_by_tiv(df, variables=None):
    if variables is None:
        variables = [
            "brain",
            "white",
            "grey",
            "csf_all",
            "csf_peripheral",
            "ventricle_volume",
            "choroid_volume",
        ]

    for var in variables:
        new_var = f"n-{var}"
        df[new_var] = df[var] / df["tiv"]

    return df


def zscore(df, skip_vars=None):
    if skip_vars is None:
        skip_vars = []
    df_z = df.copy()
    numeric_cols = df.select_dtypes(include="number").columns
    numeric_cols = numeric_cols[~numeric_cols.isin(skip_vars)]
    df_z[numeric_cols] = df_z[numeric_cols].apply(stats.zscore, nan_policy="omit")
    return df_z


#! will figure something out for boxcox and yeojohnson later if necessary: they both return a 2-tuple
transforms = {
    "log": np.log,
    "log10": np.log10,
    "log1p": np.log1p,
    "sqrt": np.sqrt,
    "square": np.square,
    "boxcox": stats.boxcox,
    "yeojohnson": stats.yeojohnson,
}


def transform_variables(df: pd.DataFrame, var_list: dict[str, str], rename=True):
    new_df = df.copy()
    for var, transform in var_list.items():
        if rename:
            new_name = f"{var}_{transform}"
        else:
            new_name = var
        new_df[new_name] = transforms[transform](new_df[var])
    return new_df


def subject_to_subid(subject):
    if not isinstance(subject, str):
        return None
    re_match = re.match(r"ms(\d{4})", subject)
    if re_match:
        return_val = int(re_match[1])
        return return_val
    else:
        return None


def set_prl_levels(df):
    prl_levels = [range(0, 1), range(1, 3), range(3, 5), range(5, df["PRL"].max() + 1)]
    df.loc[:, ["PRL_LEVEL"]] = None
    for i, level in enumerate(prl_levels):
        df.loc[df["PRL"].isin(level), ["PRL_LEVEL"]] = i
    df.loc[:, ["PRL_LEVEL"]] = pd.Categorical(df["PRL_LEVEL"], ordered=True)

    return df


def set_has_prl(df):
    df = df.copy()
    df.loc[df["PRL"] > 0, "HAS_PRL"] = 1
    df.loc[df["PRL"] == 0, "HAS_PRL"] = 0
    return df



def get_colors():
    colors = {
        "dark red1": "#eb3131",
        "light red1": "#eb7171",
        "dark blue1": "#1f4294",
        "light blue1": "#7a9df0",
        "dark green1": "#2e6023",
        "light green1": "#6dba5c",
        "dark purple1": "#8C1FA7",
        "light purple1": "#BD49DA",
    }
    return colors


def nifti_name(filename: str) -> str:
    # for a substitution could use:  s/\.nii(?:\.gz)?$//
    re_str = re.compile(r"^(.+?)(?:\.nii(?:\.gz)?)?$")
    return re_str.match(filename)[1]





def residualize_structs(model_data, dependent_var, independent_vars):
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



def read_pyprocess_output(p):
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    p.summary()
    sys.stdout = original_stdout
    output = captured_output.getvalue()
    outcome_models_pattern = r"\*+ OUTCOME MODELS \*+\n(.*?)\n(?=\*+|$)"
    outcome_model = re.search(outcome_models_pattern, output, re.DOTALL).group(1)

    direct_indirect_pattern = r"\*+ DIRECT AND INDIRECT EFFECTS \*+\n(.*?)$"
    direct_indirect = re.search(direct_indirect_pattern, output, re.DOTALL)
    mediation_model = direct_indirect.group(1)
    return outcome_model, mediation_model

#! keep the following code for my reference
# def run_R_script_old(p1, p2, p12, nobs):
#     model_data = data

#     disease_group = "MS"
#     model_data = model_data[model_data["dz_type3"] == disease_group]

#     models = {}
#     models["medial"] = sm.OLS.from_formula(
#         "medial ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()
#     models["posterior"] = sm.OLS.from_formula(
#         "posterior ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()
#     models["anterior"] = sm.OLS.from_formula(
#         "anterior ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()
#     models["ventral"] = sm.OLS.from_formula(
#         "ventral ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()
#     models["THALAMUS_1"] = sm.OLS.from_formula(
#         "THALAMUS_1 ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()
#     models["LV"] = sm.OLS.from_formula(
#         "LV ~ periCSF + age + Female + tiv", data=model_data
#     ).fit()

#     nobs = models["LV"].nobs

#     structs = ["posterior", "medial", "anterior", "ventral"]
#     working_structs = structs.copy()

#     R_cmd = "# Regressing LV residuals controlling for peripheral CSF volume\n\nresult_text <- ''\n"
#     pearson_results = {}
#     for i, struct1 in enumerate(structs):
#         working_structs = working_structs[1:]
#         for struct2 in working_structs:
#             p1, pval1 = stats.pearsonr(models[struct1].resid, models["LV"].resid)
#             pearson_results[struct1] = (p1, pval1)
#             p2, pval2 = stats.pearsonr(models[struct2].resid, models["LV"].resid)
#             pearson_results[struct2] = (p2, pval2)
#             p12, pval12 = stats.pearsonr(models[struct1].resid, models[struct2].resid)

#             if abs(p1) > abs(p2):
#                 sign = ">"
#             else:
#                 sign = "<"
#             R_cmd += textwrap.dedent(f"""
#             comparison <- '{struct1} {sign} {struct2}'
#             p <- test2r.t2({p1:0.3}, {p2:0.3}, {p12:0.3}, {nobs})$p_value
#             result_text <- paste(result_text, sprintf("%s, p=%.2e", comparison, p), sep='\\n')
#             """)

#     R_cmd += "\ncat(result_text)\n"

#     pearson_results["THALAMUS_1"] = stats.pearsonr(
#         models["THALAMUS_1"].resid, models["LV"].resid
#     )

#     # Medial has a stronger association than THALAMUS_1, so just test this one
#     p1 = pearson_results["THALAMUS_1"][0]
#     p2 = pearson_results["medial"][0]
#     p12 = stats.pearsonr(models["medial"].resid, models["THALAMUS_1"].resid).statistic
#     comparison = "'medial > THALAMUS_1'"
#     R_cmd += (
#         f"comparison <- {comparison}\n"
#         f"p <- test2r.t2({p1:0.3}, {p2:0.3}, {p12:0.3}, {nobs})$p_value\n"
#         f'result_text <- sprintf("%s, p=%.2e", comparison, p)'
#     )

#     pyperclip.copy(R_cmd)

#     print(f"Disease group: {disease_group}")
#     for struct in ["THALAMUS_1"] + structs:
#         print(
#             f"struct: {struct}, r: {pearson_results[struct][0]:0.3}, pval: {pearson_results[struct][1]:0.3}"
#         )