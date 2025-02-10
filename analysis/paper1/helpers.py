import pandas as pd
from mri_data import file_manager as fm
from pathlib import Path
import re

msmri_home = Path("/home/srs-9/Projects/ms_mri")
msmri_datadir = msmri_home / "data"
monai_analysis_dir = msmri_home / "monai_analysis"

analysis_folders = {
    "t1": "choroid_pineal_pituitary_T1-1",
    "flair": "choroid_pineal_pituitary_FLAIR-1"
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
    

def clean_df(df):
    pass


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
    df.loc[:, ["EDSS"]] = pd.Categorical(df["extracted_EDSS"], ordered=True)
    return df


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

    