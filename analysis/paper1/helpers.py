import pandas as pd
from mri_data import file_manager as fm
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from pathlib import Path
import re
import statsmodels.api as sm
import numpy as np
from scipy import stats

msmri_home = Path("/home/srs-9/Projects/ms_mri")
msmri_datadir = msmri_home / "data"
monai_analysis_dir = msmri_home / "monai_analysis"

analysis_folders = {
    "t1": "choroid_pineal_pituitary_T1-1",
    "flair": "choroid_pineal_pituitary_FLAIR-1",
}


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


def fix_edss(df):
    df.loc[:, "extracted_EDSS"] = [
        float(val) if val != "." else None for val in df["extracted_EDSS"]
    ]  #! figure out what to do with "."
    df = df.rename(columns={"extracted_EDSS": "EDSS"})
    return df


# ['MS', '!MS', 'UNK', 'RIS']
def set_dz_type2(df):
    df.loc[:, "dz_type2"] = df["ms_type"]
    df.loc[df["ms_type"].isin(["NIND", "OIND", "HC"]), "dz_type2"] = "!MS"
    ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "CIS", "RRMS"]
    df.loc[df["ms_type"].isin(ms_subtypes), "dz_type2"] = "MS"
    return df


# ['MS', 'NIND', 'UNK', 'HC', 'OIND', 'RIS']
def set_dz_type3(df):
    df.loc[:, "dz_type3"] = df["ms_type"]
    ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "RRMS", "CIS"]
    df.loc[df["ms_type"].isin(ms_subtypes), "dz_type3"] = "MS"
    return df


def set_dz_type5(df):
    df.loc[:, "dz_type5"] = df["ms_type"]
    df.loc[df["ms_type"].isin(["CIS", "RRMS"]), "dz_type5"] = "RMS"
    df.loc[df["ms_type"].isin(["PPMS", "SPMS", "RPMS", "PRMS"]), "dz_type5"] = "PMS"
    return df


def clean_df(df):
    not_nas = (
        ~df["pineal_volume"].isna()
        & ~df["choroid_volume"].isna()
        & ~df["pituitary_volume"].isna()
    )
    df = df.loc[not_nas, :]

    df.loc[df["PRL"] == "#VALUE!", "PRL"] = None
    df.loc[:, "PRL"] = [
        int(val) if val != "#VALUE!" and val is not None else None for val in df["PRL"]
    ]
    df.loc[df["dzdur"] == "#VALUE!", "dzdur"] = None
    df.loc[:, "dzdur"] = df["dzdur"].astype("float")

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
        a_edss = edsss[(ages >= age-2) & (ages <= age+2)]
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
    ax.scatter(lines1.get_xdata(), lines1.get_ydata(), color=[.2, .2, .2])
    ax.plot(lines2.get_xdata(), lines2.get_ydata(), color=[0, 0, 0])
    # ax = fig.get_axes()[0]
    ax.set_facecolor([.9, .9, .9])
    # ax.set_alpha(0)
    fig.patch.set_alpha(0)
    ax.set_xlabel(f"e({var} | others)", fontsize=14)
    ax.set_ylabel("")

    return fig, ax


def prepare_data(data_file):
    df = pd.read_csv(data_file)
    df = df.set_index("subid")

    df = set_dz_type5(df)
    df = set_dz_type3(df)
    df = set_dz_type2(df)
    df = fix_edss(df)
    df = clean_df(df)

    keep_cols = [
        "subject",
        "age",
        "sex",
        "ms_type",
        "dz_type2",
        "dz_type3",
        "dz_type5",
        "dzdur",
        "EDSS",
        "MSSS",
        "gMSSS",
        "ARMSS",
        "DMT_score",
        "DMT_hx_all",
        "flair_contrast",
        "lesion_count",
        "lesion_vol_cubic",
        "PRL",
        "tiv",
        "choroid_volume",
        "pineal_volume", 
        "pituitary_volume"
    ]

    df = df.loc[:, keep_cols]
    df = pd.concat((df, pd.get_dummies(df["sex"])), axis=1)

    df.loc[:, "lesion_vol_logtrans"] = np.log(df["lesion_vol_cubic"])
    df.loc[:, "edss_sqrt"] = np.sqrt(df["EDSS"].astype("float"))
    df.loc[:, "msss_sqrt"] = np.sqrt(df["MSSS"])
    df.loc[:, "armss_sqrt"] = np.sqrt(df["ARMSS"])
    df.loc[:, "gmsss_sqrt"] = np.sqrt(df["gMSSS"])

    vars = [
        "age",
        "Female",
        "dzdur",
        "EDSS",
        "MSSS",
        "gMSSS",
        "ARMSS",
        "edss_sqrt",
        "msss_sqrt",
        "armss_sqrt",
        "gmsss_sqrt",
        "DMT_score",
        "DMT_hx_all",
        "lesion_count",
        "lesion_vol_cubic",
        "lesion_vol_logtrans",
        "PRL",
        "tiv",
        "choroid_volume",
    ]

    for var in vars:
        df[var] = pd.to_numeric(df[var])

    vars_to_center = ["edss_sqrt", "lesion_vol_logtrans", "lesion_vol_cubic", "dzdur", "choroid_volume"]

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