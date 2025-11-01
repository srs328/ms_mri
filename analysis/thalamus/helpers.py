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


def load_df():
    choroid_volumes = pd.read_csv(
    "/home/srs-9/Projects/ms_mri/data/choroid_aschoplex_volumes.csv", index_col="subid"
    )
    ventricle_volumes = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/analysis/paper1/data0/ventricle_volumes.csv",
        index_col="subid",
    )
    csf_volumes = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/csf_volumes2.csv",
        index_col="subid",
    )
    third_ventricle_width = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/third_ventricle_width.csv",
        index_col="subid",
    )

    tiv = pd.read_csv("/home/srs-9/Projects/ms_mri/data/tiv_data.csv", index_col="subid")

    df = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/data/clinical_data_processed.csv", index_col="subid"
    )
    sdmt = pd.read_csv(
        "/home/srs-9/Projects/ms_mri/analysis/thalamus/SDMT_sheet.csv", index_col="subid"
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
    rename_columns = {
        "ventricle_volume": "LV",
        "choroid_volume": "CP",
        "peripheral": "periCSF",
        "all": "allCSF",
        "third_ventricle": "thirdV",
        "fourth_ventricle": "fourthV",
        "aseg_csf": "asegCSF",
        "third_ventricle_width": "thirdV_width"
    }
    df.rename(columns=rename_columns, inplace=True)

    return df


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


def fix_edss(df):
    df.loc[:, "extracted_EDSS"] = [
        float(val) if val != "." else None for val in df["extracted_EDSS"]
    ]  #! figure out what to do with "."
    df["extracted_EDSS"] = df["extracted_EDSS"].astype("float")
    return df


def do_sqrt_transform(df, vars):
    for var in vars:
        df[f"{var}_sqrt"] = np.sqrt(df[var])
    return df


def do_log_transform(df, vars):
    for var in vars:
        df[f"{var}_logtrans"] = np.log(df[var])
    return df


def do_center(df, vars):
    for var in vars:
        df[f"{var}_cent"] = df[var] - df[var].mean()
    return df


def do_scale(df, vars):
    for var in vars:
        df[f"{var}_scale"] = df[var] / df[var].mean()
    return df


# ['MS', '!MS', 'UNK']
def set_dz_type2(df):
    df.loc[:, "dz_type2"] = df["ms_type"]
    df.loc[df["ms_type"].isin(["NIND", "OIND", "HC"]), "dz_type2"] = "!MS"
    ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "CIS", "RRMS", "RIS"]
    df.loc[df["ms_type"].isin(ms_subtypes), "dz_type2"] = "MS"
    return df


# ['MS', 'NIND', 'UNK', 'HC', 'OIND']
def set_dz_type3(df):
    df.loc[:, "dz_type3"] = df["ms_type"]
    ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "RRMS", "CIS", "RIS"]
    df.loc[df["ms_type"].isin(ms_subtypes), "dz_type3"] = "MS"
    return df


def set_dz_type5(df):
    df.loc[:, "dz_type5"] = df["ms_type"]
    df.loc[df["ms_type"].isin(["CIS", "RIS", "RRMS"]), "dz_type5"] = "RMS"
    df.loc[df["ms_type"].isin(["PPMS", "SPMS", "RPMS", "PRMS"]), "dz_type5"] = "PMS"
    return df


def clean_dz_type(df, col="dz_type5", keeps=None):
    if keeps is None:
        keeps = ["RMS", "PMS", "NIND", "OIND"]
    return df[df[col].isin(keeps)]


def clean_df(df: pd.DataFrame):
    # not_nas = (
    #     ~df["pineal_volume"].isna()
    #     & ~df["choroid_volume"].isna()
    #     & ~df["pituitary_volume"].isna()
    # )
    # df = df.loc[not_nas, :]

    df.loc[df["PRL"] == "#VALUE!", "PRL"] = None
    df.loc[df["PRL"].isna(), "PRL"] = None
    df.loc[:, "PRL"] = [
        int(val) if val != "#VALUE!" and val is not None else None for val in df["PRL"]
    ]
    df.loc[df["dzdur"] == "#VALUE!", "dzdur"] = None
    df.loc[:, "dzdur"] = df["dzdur"].astype("float")
    df = pd.concat((df, pd.get_dummies(df["sex"], dtype="int")), axis=1)

    return df


def get_mri_edss_delta(df):
    date_str = "%m/%d/%Y"
    for i, row in df.iterrows():
        try:
            edss_date = datetime.strptime(row["edss_date_closest"], date_str)
        except (ValueError, TypeError):
            edss_date = pd.NA
        try:
            mri_date = datetime.strptime(row["mri_date_closest"], date_str)
        except (ValueError, TypeError):
            mri_date = pd.NA
        delta = edss_date - mri_date
        if isinstance(delta, timedelta):
            df.loc[i, "edss_mri_delta"] = delta.days
        else:
            df.loc[i, "edss_mri_delta"] = None
    return df


def norm_volumes(df):
    df["norm_choroid_volume"] = df["choroid_volume"] / df["tiv"] * 1000
    return df


# not necessary for newest data files in analysis/paper1/data
def load_data(modality):
    analysis_dir = analysis_folders[modality]
    df_vols = pd.read_csv(analysis_dir / "clinical_data_full.csv")
    df_vols = df_vols.set_index("subid")
    keep_cols = [
        "choroid_volume",
        "pineal_volume",
        "pituitary_volume",
        "tiv",
        "flair_contrast",
        "label",
        "scan_folder",
        "age",
    ]

    not_nas = (
        ~df_vols["pineal_volume"].isna()
        & ~df_vols["choroid_volume"].isna()
        & ~df_vols["pituitary_volume"].isna()
    )
    df_vols = df_vols.loc[not_nas, keep_cols]

    df_full = pd.read_csv(msmri_datadir / "Clinical_Data_All_updated.csv")
    df_full.insert(0, "subid", df_full["ID"].map(subject_to_subid))
    df_full = df_full.set_index("subid")

    df = pd.merge(
        df_vols,
        df_full.loc[:, ~df_full.columns.isin(df_vols.columns)],
        how="outer",
        on="subid",
    )

    df.loc[df["PRL"] == "#VALUE!", "PRL"] = None
    df.loc[:, "PRL"] = [
        int(val) if val != "#VALUE!" and val is not None else None for val in df["PRL"]
    ]
    df.loc[df["dzdur"] == "#VALUE!", "dzdur"] = None

    df = set_prl_levels(df)

    df.loc[:, ["norm_choroid_volume"]] = df["choroid_volume"] / df["tiv"]
    df.loc[:, ["norm_pineal_volume"]] = df["pineal_volume"] / df["tiv"]
    df.loc[:, ["norm_pituitary_volume"]] = df["pituitary_volume"] / df["tiv"]


def get_armss(edsss, ages):
    armsss = edsss
    for ind, edss, age in zip(edsss.index, edsss, ages):
        a_edss = edsss[(ages >= age - 2) & (ages <= age + 2)]
        ranks = a_edss.rank()
        armsss.loc[ind] = ranks.loc[ind] / (len(a_edss) + 1) * 10

    return armsss


def plot_partial_regress(res, var):
    fig = sm.graphics.plot_partregress_grid(res, exog_idx=[var])
    ax = fig.get_axes()[0]
    lines1 = ax.lines[0]
    lines2 = ax.lines[1]
    plt.close()
    # fig = plt.figure(figsize=(9, 6))
    fig, ax = plt.subplots()
    ax.scatter(lines1.get_xdata(), lines1.get_ydata(), color=[0.2, 0.2, 0.2])
    ax.plot(lines2.get_xdata(), lines2.get_ydata(), color=[0, 0, 0])
    # ax = fig.get_axes()[0]
    ax.set_facecolor([0.9, 0.9, 0.9])
    # ax.set_alpha(0)
    fig.patch.set_alpha(0)
    ax.set_xlabel(f"e({var} | others)", fontsize=14)
    ax.set_ylabel("")

    return fig, ax


def get_regression_y0(data, res, x, outcome):
    coef = res.params

    other_vars = coef.index[~coef.index.isin([x, "Intercept"])]
    other_terms = np.sum(coef[other_vars] * data[other_vars].mean())
    conf_int = res.conf_int()

    x_data = np.linspace(data[x].min(), data[x].max(), 100)
    y_pred = x_data * coef[x] + other_terms + coef["Intercept"]

    y_upper = x_data * conf_int.loc[x, 1] + other_terms + coef["Intercept"]

    y_lower = x_data * conf_int.loc[x, 0] + other_terms + coef["Intercept"]
    # upper_error = y_upper - y
    # lower_error = y - y_lower

    # fig, ax = plt.subplots()
    # ax.scatter(data[x], data[outcome])
    # ax.plot(x_data, y_pred)
    # ax.fill_between(x_data, y_lower, y_upper, alpha=0.2)

    return x_data, y_pred, (y_lower, y_upper)


def get_regression_y(data, res, x, outcome):
    other_vars = set(res.model.exog_names) - set(["Intercept", x])
    d = {var: [data[var].mean()] for var in other_vars}
    d[x] = np.linspace(data[x].min(), data[x].max())
    test_data = (
        pd.MultiIndex.from_product(d.values(), names=d.keys())
        .to_frame()
        .reset_index(drop=True)
    )
    pred = res.get_prediction(test_data).summary_frame(alpha=0.05)
    y_pred, y_upper, y_lower = (
        pred["mean"],
        pred["mean_ci_upper"],
        pred["mean_ci_lower"],
    )

    x_data = test_data[x]
    # upper_error = y_upper - y
    # lower_error = y - y_lower

    # fig, ax = plt.subplots()
    # ax.scatter(data[x], data[outcome])
    # ax.plot(x_data, y_pred)
    # ax.fill_between(x_data, y_lower, y_upper, alpha=0.2)

    return x_data, y_pred, (y_lower, y_upper)


# check https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html
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

    # the histograms
    xbins = np.linspace(np.min(x), np.max(x), nbins)
    ybins = np.linspace(np.min(y), np.max(y), nbins)
    ax_histx.hist(x, bins=xbins, color=light_color, density=True)
    ax_histy.hist(
        y, bins=ybins, orientation="horizontal", color=light_color, density=True
    )

    # kde to plot on histograms
    densityx = stats.gaussian_kde(x.dropna())
    densityy = stats.gaussian_kde(y.dropna())
    xx = np.linspace(np.min(x), np.max(x), 50)
    xy = np.linspace(np.min(y), np.max(y), 50)
    ax_histx.plot(xx, densityx(xx), color=dark_color)
    ax_histy.plot(densityy(xy), xy, color=dark_color)


def plot_reg_var2(data, res, x, outcome):
    coef = res.params

    other_vars = coef.index[~coef.index.isin([x, "Intercept"])]
    other_terms = np.sum(coef[other_vars] * data[other_vars].mean())
    conf_int = res.conf_int()

    x_data = np.linspace(data[x].min(), data[x].max(), 100)
    y_pred = x_data * coef[x] + other_terms + coef["Intercept"]

    y_upper = x_data * conf_int.loc[x, 1] + other_terms + coef["Intercept"]

    y_lower = x_data * conf_int.loc[x, 0] + other_terms + coef["Intercept"]
    # upper_error = y_upper - y
    # lower_error = y - y_lower

    fig, ax = plt.subplots()
    ax.scatter(data[x], data[outcome])
    ax.plot(x_data, y_pred)
    ax.fill_between(x_data, y_lower, y_upper, alpha=0.2)

    return fig


def moderation_y(data, res, x_name, m_name):
    coef = res.params
    conf_int = res.conf_int()

    reg = re.compile(r"(\w+)\:(\w+)")
    regression_data = {}
    for name in coef.index:
        if name == "Intercept":
            continue
        mat = reg.match(name)
        if mat is None:
            regression_data[name] = data[name]
        else:
            regression_data[name] = data[mat[1]] * data[mat[2]]
            inter_name = name
    regression_data = pd.DataFrame(regression_data)

    other_vars = coef.index[~coef.index.isin([x_name, m_name, inter_name, "Intercept"])]
    other_terms = np.sum(coef[other_vars] * regression_data.loc[:, other_vars].mean())

    m_vals = [
        data[m_name].mean() - data[m_name].std(),
        data[m_name].mean(),
        data[m_name].mean() + data[m_name].std(),
    ]

    x_rng = np.linspace(data[x_name].min(), data[x_name].max(), 100)
    y_lvls = []
    for m_val in m_vals:
        y = (
            x_rng * coef[x_name]
            + m_val * coef[m_name]
            + coef[inter_name] * m_val * x_rng
            + other_terms
            + coef["Intercept"]
        )
        y_lower = (
            x_rng * conf_int.loc[x_name, 0]
            + m_val * coef[m_name]
            + coef[inter_name] * m_val * x_rng
            + other_terms
            + coef["Intercept"]
        )
        y_upper = (
            x_rng * conf_int.loc[x_name, 1]
            + m_val * coef[m_name]
            + coef[inter_name] * m_val * x_rng
            + other_terms
            + coef["Intercept"]
        )
        y_lvls.append((y, y_lower, y_upper))

    return x_rng, y_lvls


def moderation_y_test(data, res, x_name, m_name):
    coef = res.params
    conf_int = res.conf_int()

    regression_data = {}
    for name in coef.index:
        if name == "Intercept":
            continue
        regression_data[name] = data[name]

    regression_data = pd.DataFrame(regression_data)

    other_vars = coef.index[~coef.index.isin([x_name, m_name, "Intercept"])]
    other_terms = np.sum(coef[other_vars] * regression_data.loc[:, other_vars].mean())

    m_vals = [
        data[m_name].mean() - data[m_name].std(),
        data[m_name].mean(),
        data[m_name].mean() + data[m_name].std(),
    ]

    x_rng = np.linspace(data[x_name].min(), data[x_name].max(), 100)
    y_lvls = []
    for m_val in m_vals:
        y = (
            x_rng * coef[x_name]
            + m_val * coef[m_name]
            + other_terms
            + coef["Intercept"]
        )
        y_lower = (
            x_rng * conf_int.loc[x_name, 0]
            + m_val * coef[m_name]
            + other_terms
            + coef["Intercept"]
        )
        y_upper = (
            x_rng * conf_int.loc[x_name, 1]
            + m_val * coef[m_name]
            + other_terms
            + coef["Intercept"]
        )
        y_lvls.append((y, y_lower, y_upper))

    return x_rng, y_lvls


def plot_moderation(x_data, y_data, x_rng, y_lvls):
    plt.scatter(x_data, y_data, s=5)
    plt.plot(x_rng, y_lvls[0], label="m-sd", linestyle="--")
    plt.plot(x_rng, y_lvls[1], label="m", linestyle="-")
    plt.plot(x_rng, y_lvls[2], label="m+sd", linestyle=":")

    plt.legend()


def prepare_data(data_file):
    df = pd.read_csv(data_file)
    df = df.set_index("subid")

    df = df.loc[:, keep_cols]
    df = set_dz_type5(df)
    df = set_dz_type3(df)
    df = set_dz_type2(df)
    df = fix_edss(df)
    df = clean_df(df)

    df = pd.concat((df, pd.get_dummies(df["sex"])), axis=1)

    df.loc[:, "lesion_vol_logtrans"] = np.log(df["lesion_vol_cubic"])
    df.loc[:, "edss_sqrt"] = np.sqrt(df["EDSS"].astype("float"))
    df.loc[:, "msss_sqrt"] = np.sqrt(df["MSSS"])
    df.loc[:, "armss_sqrt"] = np.sqrt(df["ARMSS"])
    df.loc[:, "gmsss_sqrt"] = np.sqrt(df["gMSSS"])

    for var in vars:
        df[var] = pd.to_numeric(df[var])

    for var in vars_to_center:
        df[f"{var}_cent"] = df[var] - df[var].mean()

    centered_vars = [f"{var}_cent" for var in vars_to_center]
    vars.extend(centered_vars)

    df_z = df[vars].astype("float")
    df_z[df.columns[~df.columns.isin(vars)]] = df[df.columns[~df.columns.isin(vars)]]
    df_z = df_z[df.columns]
    df_z[vars] = df_z[vars].apply(stats.zscore, nan_policy="omit")

    data = df[vars].astype("float")
    data_z = data[vars].apply(stats.zscore, nan_policy="omit")

    return df, df_z, data, data_z


def load_radiomics_data(path):
    df = pd.read_csv(path)


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
