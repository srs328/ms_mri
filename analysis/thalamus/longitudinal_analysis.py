# %% [imports and setup]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.insert(0, "/home/srs-9/Projects/ms_mri/analysis/thalamus/helpers")

import helpers
import utils


#%%

# Load longitudinal volumes
df_long = pd.read_csv("/home/srs-9/Projects/ms_mri/data/longitudinal/full_volumes3.csv")
df_long['time1'] = pd.to_datetime(df_long['time1'], format='%Y%m%d')
df_long['time2'] = pd.to_datetime(df_long['time2'], format='%Y%m%d')
df_long['interval_years'] = (df_long['time2'] - df_long['time1']).dt.days / 365.25

# Load baseline covariates (adjust path as needed)
# Expected columns: subid, T2LV, dzdur, age, Female, tiv, CP
df_base = utils.load_data("/home/srs-9/Projects/ms_mri/analysis/thalamus/results/data.csv")
df_base = df_base.reset_index()

# Merge on subid
df = df_long.merge(df_base, on='subid', how='inner')
print(f"N after merge: {len(df)}")
print(f"Interval range: {df['interval_years'].min():.2f} – {df['interval_years'].max():.2f} years")

skip_subs = [1027, 1264, 1163]
df = df[~df['subid'].isin(skip_subs)]

df = df[df['dz_type2'] == "MS"]
# %% [compute annualized change scores]
# Using annualized % change to account for variable follow-up intervals.
# Annualized % = ((V2 - V1) / V1) / interval * 100
# This is our primary longitudinal outcome.

structures = {
    'THALAMUS_1': 'Whole Thalamus',
    'Pul_8':      'Pulvinar',
    'MD_Pf_12':   'MD/Parafascicular',
    'AV_2':       'Anterior Ventral',
    'VLP_6':      'VLP',
    'VPL_7':      'VPL',
    'CM_11':      'Centromedian',
}

for col_prefix, label in structures.items():
    v1 = df[f'{col_prefix}_time1']
    v2 = df[f'{col_prefix}_time2']
    pct_change = (v2 - v1) / v1 * 100
    df[f'{col_prefix}_pct_change'] = pct_change
    df[f'{col_prefix}_ann_pct_change'] = pct_change / df['interval_years']

print(df[[f'{col_prefix}_ann_pct_change' for col_prefix in structures]].describe().round(3))


# %% [QC: flag implausible volumes and large change outliers]
# Whole thalamus bilateral should be roughly 5500-9000 mm³ in adults.
# Values outside this range suggest segmentation failure.
# Also flag subjects with >20% change (annualized) as likely failures.

THAL_MIN, THAL_MAX = 5500, 13000
THAL_MIN, THAL_MAX = 4000, 13000
ANN_CHANGE_THRESH = 5  # % per year — biologically implausible

df['qc_thal_t1_range'] = df['THALAMUS_1_time1'].between(THAL_MIN, THAL_MAX)
df['qc_thal_t2_range'] = df['THALAMUS_1_time2'].between(THAL_MIN, THAL_MAX)
df['qc_ann_change']    = df['THALAMUS_1_ann_pct_change'].abs() < ANN_CHANGE_THRESH
df['qc_pass']          = df['qc_thal_t1_range'] & df['qc_thal_t2_range'] & df['qc_ann_change']

print(f"\nQC summary:")
print(f"  Fail thal range at T1:    {(~df['qc_thal_t1_range']).sum()}")
print(f"  Fail thal range at T2:    {(~df['qc_thal_t2_range']).sum()}")
print(f"  Fail ann change threshold:{(~df['qc_ann_change']).sum()}")
print(f"  Total QC pass:            {df['qc_pass'].sum()} / {len(df)}")

# Inspect failures
df_fail = df[~df['qc_pass']][['subid', 'interval_years',
                               'THALAMUS_1_time1', 'THALAMUS_1_time2',
                               'THALAMUS_1_pct_change', 'THALAMUS_1_ann_pct_change']]
print("\nFailed subjects:")
print(df_fail.to_string())

df_qc = df[df['qc_pass']].copy()
print(f"\nProceeding with N={len(df_qc)} after QC")


# %% [QC visualization: volume distributions and change distributions]
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle('QC: Volume and Change Distributions', fontsize=13, fontweight='bold')

struct_keys = list(structures.keys())

# Row 1: T1 vs T2 scatter for 3 structures
for ax, key in zip(axes[0], struct_keys[:3]):
    label = structures[key]
    v1 = df_qc[f'{key}_time1']
    v2 = df_qc[f'{key}_time2']
    ax.scatter(v1, v2, alpha=0.5, s=20)
    lims = [min(v1.min(), v2.min()), max(v1.max(), v2.max())]
    ax.plot(lims, lims, 'r--', lw=1, label='no change')
    ax.set_xlabel('T1 volume (mm³)')
    ax.set_ylabel('T2 volume (mm³)')
    ax.set_title(label)
    ax.legend(fontsize=8)

# Row 2: annualized % change distributions
for ax, key in zip(axes[1], struct_keys[:3]):
    label = structures[key]
    vals = df_qc[f'{key}_ann_pct_change']
    ax.hist(vals, bins=20, edgecolor='white', color='steelblue')
    ax.axvline(0, color='red', lw=1, ls='--')
    ax.axvline(vals.mean(), color='orange', lw=1.5, ls='-', label=f'mean={vals.mean():.2f}%/yr')
    ax.set_xlabel('Annualized % change')
    ax.set_title(label)
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('qc_distributions.png', dpi=150)
plt.show()


# %% [QC: test for expected atrophy direction]
# In MS, we expect thalamic atrophy (negative change) at the group level.
# A one-sample t-test against zero is a basic sanity check.
# We also check whether nuclei with expected greater vulnerability (MD, Pul)
# show more atrophy than peripheral nuclei (VPL, VLa).

print("One-sample t-tests (H0: no change):")
print(f"{'Structure':<25} {'Mean %/yr':>10} {'t':>8} {'p':>8}")
print("-" * 55)
for key, label in structures.items():
    vals = df_qc[f'{key}_ann_pct_change'].dropna()
    t, p = stats.ttest_1samp(vals, 0)
    print(f"{label:<25} {vals.mean():>10.3f} {t:>8.3f} {p:>8.4f}")


# %% [validation: T2LV at baseline predicts thalamic atrophy rate]
# The key validation: subjects with higher T2LV (greater lesion burden) at
# baseline should show faster thalamic atrophy over follow-up.
# This is a well-replicated finding in the MS literature.
#
# We use T2LV at T1 only (not change in T2LV) because:
#   1. Baseline lesion burden reflects accumulated damage driving ongoing atrophy
#   2. Using only T1 avoids any circularity if lesion change correlates with
#      thalamic change through shared measurement error
#   3. Most validation studies use baseline T2LV as the predictor
#
# We control for: interval_years, age, tiv, disease duration, sex
# Using log(T2LV) because T2LV is typically right-skewed

df_qc['thal_ann_change_z'] = stats.zscore(df_qc['THALAMUS_1_ann_pct_change'])
df_qc['log_T2LV_z']        = stats.zscore(df_qc['T2LV_log1p'], nan_policy="omit")
df_qc['age_z']             = stats.zscore(df_qc['age'])
df_qc['tiv_z']             = stats.zscore(df_qc['tiv'])
df_qc['dzdur_z']           = stats.zscore(df_qc['dzdur'])

formula = 'thal_ann_change_z ~ log_T2LV_z + age_z + tiv_z + dzdur_z + interval_years + Female'
model = smf.ols(formula, data=df_qc).fit(cov_type='HC3')
print(model.summary())


# %% [validation: T2LV -> thalamic atrophy visualization]
# Partial regression plot of T2LV effect after controlling for covariates

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

# Left: raw scatter with regression line (unadjusted, for intuition)
ax = axes[0]
x = df_qc['log_T2LV']
y = df_qc['THALAMUS_1_ann_pct_change']
ax.scatter(x, y, alpha=0.5, s=20, color='steelblue')
m, b, r, p, _ = stats.linregress(x, y)
xline = np.linspace(x.min(), x.max(), 100)
ax.plot(xline, m * xline + b, 'r-', lw=1.5)
ax.set_xlabel('log(T2LV + 1)')
ax.set_ylabel('Annualized thalamic change (%/yr)')
ax.set_title(f'T2LV → Thalamic Atrophy Rate\nr={r:.3f}, p={p:.4f} (unadjusted)')

# Right: partial regression plot (adjusted)
ax = axes[1]
sm.graphics.plot_partregress(
    'thal_ann_change_z', 'log_T2LV_z',
    ['age_z', 'tiv_z', 'dzdur_z', 'interval_years', 'Female'],
    data=df_qc, ax=ax, obs_labels=False
)
ax.set_title('Partial Regression (adjusted)')
ax.set_xlabel('log(T2LV) | covariates')
ax.set_ylabel('Thalamic atrophy rate | covariates')

plt.tight_layout()
plt.savefig('t2lv_validation.png', dpi=150)
plt.show()


# %% [validation: nucleus-specific vulnerability gradient]
# If the segmentations are valid, nuclei known to be most vulnerable in MS
# (MD, Pul — periventricular/CSF-adjacent) should show greater atrophy
# than less vulnerable nuclei (VPL, GP — more peripheral).
# This is both a biological validation and relevant to your distance hypothesis.

print("Annualized atrophy by nucleus (QC-passed subjects):")
print(f"{'Nucleus':<25} {'N':>5} {'Mean %/yr':>10} {'SD':>8} {'p (vs 0)':>10}")
print("-" * 62)
for key, label in structures.items():
    col = f'{key}_ann_pct_change'
    if col not in df_qc.columns:
        continue
    vals = df_qc[col].dropna()
    t, p = stats.ttest_1samp(vals, 0)
    print(f"{label:<25} {len(vals):>5} {vals.mean():>10.3f} {vals.std():>8.3f} {p:>10.4f}")


# %% [nucleus-specific vulnerability: visualization]
# Bar chart of mean annualized change ± SE, sorted by atrophy magnitude.
# Nuclei expected to be more vulnerable should cluster toward more negative values.

means, sems, labels_sorted = [], [], []
for key, label in structures.items():
    col = f'{key}_ann_pct_change'
    if col not in df_qc.columns:
        continue
    v = df_qc[col].dropna()
    means.append(v.mean())
    sems.append(v.sem())
    labels_sorted.append(label)

order = np.argsort(means)
means = np.array(means)[order]
sems  = np.array(sems)[order]
labels_sorted = np.array(labels_sorted)[order]

fig, ax = plt.subplots(figsize=(9, 4))
colors = ['#d62728' if m < 0 else '#2ca02c' for m in means]
ax.barh(labels_sorted, means, xerr=sems, color=colors, alpha=0.8, capsize=3)
ax.axvline(0, color='black', lw=0.8)
ax.set_xlabel('Mean annualized volume change (%/yr)')
ax.set_title('Nucleus-Specific Atrophy Rates (QC-passed, MS)')
plt.tight_layout()
plt.savefig('nucleus_vulnerability.png', dpi=150)
plt.show()


# %% [summary: what to check before proceeding]
# 1. QC failures: visually inspect failed subjects in ITK-SNAP
#    - Very low/high T1 volumes → likely segmentation failure at that time point
#    - Very large change → could also be registration error pulling the template
# 2. T2LV validation: expect beta for log_T2LV_z to be negative (more lesions → more atrophy)
#    - If direction is wrong, something is off with the segmentations or the merge
# 3. Nucleus vulnerability: expect MD/Pul > VPL/GP in atrophy magnitude
#    - If peripheral nuclei atrophy more, worth checking template registration quality
# 4. Interval distribution is already quite tight (mean ~4.3yr) so time as covariate
#    should be well-behaved — but include it regardless

print("Done. Check output figures and model summaries above.")
print("Next step: visually QC failed subjects in ITK-SNAP before exclusion.")


def get_diff(ses2, ses1):
    return (datetime.strptime(ses, "%Y%m%d") - datetime.strptime(ses1, "%Y%m%d")).days


second_sessions = []
for sub in df_base.index:
    ses1 = subject_sessions.loc[sub, 'ses']
    ses_list = subject_sessions_longit[str(sub)]
    if len(ses_list) < 2:
        continue
    ses2 = ses1
    t_diff = 0
    for ses in ses_list:
        if (new_diff := abs(get_diff(ses, ses1) - 5*365)) < abs(get_diff(ses2, ses1) - 5*365):
            ses2 = ses
            t_diff = new_diff
        
    second_sessions.append((ses2, t_diff))