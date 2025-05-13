import pandas as pd
from pathlib import Path
import os
import re
from mri_data import file_manager as fm
import numpy as np

drive_root = fm.get_drive_root()
clinical_data_root = drive_root / "Secure_Data" / "Large"
data_dir = Path("/home/srs-9/Projects/ms_mri/analysis/thalamus/data0")

def subject_to_subid(subject):
    if not isinstance(subject, str):
        return None
    re_match = re.match(r"ms(\d{4})", subject)
    if re_match:
        return_val = int(re_match[1])
        return return_val
    else:
        return None
    
def do_sqrt_transform(df, vars):
    for var in vars:
        df[f"{var}_sqrt"] = np.sqrt(df[var])
    return df


def do_log_transform(df, vars):
    for var in vars:
        df[f"{var}_logtrans"] = np.log(df[var])
    return df

df = pd.read_csv(clinical_data_root / "Clinical_Data_All_updated.csv")
df = df.convert_dtypes()

new_columns = {
    "ID": "subject",
    "age_at_obs_start": "age",
}
df.rename(columns=new_columns, inplace=True)
df["subid"] = df["subject"].apply(subject_to_subid)
df.drop(df[df["subid"].isna()].index, inplace=True)
df["subid"] = df["subid"].astype(int)
df = df.set_index("subid")

new_columns = {}
for col in df.columns:
    new_columns[col] = col.replace(" ", "_")
df.rename(columns=new_columns, inplace=True)


# ['MS', '!MS', 'UNK']
df.loc[:, "dz_type2"] = df["ms_type"]
df.loc[df["ms_type"].isin(["NIND", "OIND", "HC"]), "dz_type2"] = "!MS"
ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "CIS", "RRMS", "RIS"]
df.loc[df["ms_type"].isin(ms_subtypes), "dz_type2"] = "MS"


# ['MS', 'NIND', 'UNK', 'HC', 'OIND']
df.loc[:, "dz_type3"] = df["ms_type"]
ms_subtypes = ["PPMS", "SPMS", "RPMS", "PRMS", "RRMS", "CIS", "RIS"]
df.loc[df["ms_type"].isin(ms_subtypes), "dz_type3"] = "MS"


# dz_type5
df.loc[:, "dz_type5"] = df["ms_type"]
df.loc[df["ms_type"].isin(["CIS", "RIS", "RRMS"]), "dz_type5"] = "RMS"
df.loc[df["ms_type"].isin(["PPMS", "SPMS", "RPMS", "PRMS"]), "dz_type5"] = "PMS"


# fix_edss
df.loc[:, "extracted_EDSS"] = [
    float(val) if val != "." else None for val in df["extracted_EDSS"]
]  
#! figure out what to do with "."
df["extracted_EDSS"] = df["extracted_EDSS"].astype("float")


# clean_df
df.loc[df["PRL"] == "#VALUE!", "PRL"] = None
# df.loc[df["PRL"].isna(), "PRL"] = None
# df.loc[:, "PRL"] = [
#     int(val) if val != "#VALUE!" and val is not None else None for val in df["PRL"]
# ]
df['PRL'] = df['PRL'].fillna('0')
df['PRL'] = df['PRL'].astype("int")
df.loc[df["dzdur"] == "#VALUE!", "dzdur"] = None
df.loc[:, "dzdur"] = df["dzdur"].astype("float")
df = pd.concat((df, pd.get_dummies(df["sex"], dtype="int")), axis=1)


# set_has_prl
df.loc[df["PRL"] > 0, "HAS_PRL"] = 1
df.loc[df["PRL"] == 0, "HAS_PRL"] = 0


df.rename(columns={"lesion_vol_cubic": "t2lv"}, inplace=True)
df = df.rename(columns={"extracted_EDSS": "EDSS"})

df = do_sqrt_transform(df, ["EDSS", "MSSS", "ARMSS", "gMSSS"])
df = do_log_transform(df, ["t2lv"])

df.to_csv(data_dir / "clinical_data_processed.csv")