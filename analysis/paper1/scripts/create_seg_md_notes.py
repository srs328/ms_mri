import pandas as pd

df = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/t1_data_full.csv", index_col="subid")
df_man = pd.read_csv("/home/srs-9/Projects/ms_mri/analysis/paper1/data0/manual_labels.csv", index_col="subid")

lines = ["# Segmentation Notes"]
for i, row in df.iterrows():
    lines.append(f"## {i}")
    if i in df_man.index:
        lines.append("*Manual cohort*")
    lines.extend(["### Choroid", "### Pineal", "### Pituitary", "---"])
    
outstr = "\n\n".join(lines)
with open("Segmentation Notes.md", 'w') as f:
    f.write(outstr)

