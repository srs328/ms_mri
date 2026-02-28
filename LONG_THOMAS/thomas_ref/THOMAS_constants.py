#!/usr/bin/env python3
"""
Paths, names, optimized hyper-parameters, and other constants for THOMAS.
"""
import os
#import shelve

# Read the environment variable containing the application's root directory
THOMAS_HOME = os.getenv('THOMAS_HOME')
if (not (THOMAS_HOME and os.path.isdir(THOMAS_HOME))):
    print("The environment variable THOMAS_HOME must be set before this program is run.")
    exit(1)

# Set path variables for code and resources:
RES_PATH = os.path.join(THOMAS_HOME, 'resources')
# assert os.path.exists(RES_PATH)

PRIOR_PATH = os.path.join(RES_PATH, 'priors')
# assert os.path.exists(PRIOR_PATH)

WMN_BIAS_IMAGE = 'WMnMPRAGE_bias_corr.nii.gz'

ORIG_TEMPLATE = os.path.join(RES_PATH, 'origtemplate.nii.gz')
# assert os.path.exists(ORIG_TEMPLATE)

ORIG_TEMPLATE_MNI_STRIPPED = os.path.join(RES_PATH, 'origtemplate_mni_stripped.nii.gz')
# assert os.path.exists(ORIG_TEMPLATE_MNI_STRIPPED)

TEMPLATE_61 = os.path.join(RES_PATH, 'templ_61x91x62.nii.gz')
# assert os.path.exists(TEMPLATE_61)

TEMPLATE_93 = os.path.join(RES_PATH, 'templ_93x187x68.nii.gz')
# assert os.path.exists(TEMPLATE_93)

TEMPLATE_93B = os.path.join(RES_PATH, 'templ_113x207x88.nii.gz')
# assert os.path.exists(TEMPLATE_93B)

MASK_61 = os.path.join(RES_PATH, 'mask_templ_61x91x62.nii.gz')
# assert os.path.exists(MASK_61)

MASK_93 = os.path.join(RES_PATH, 'mask_templ_93x187x68.nii.gz')
# assert os.path.exists(MASK_93)

MASK_93B = os.path.join(RES_PATH, 'mask_templ_93x187x68_B.nii.gz')
# assert os.path.exists(MASK_93B)

# Amount of padding to add for (default) bigger crop
UNCROP_PADDING = 10

# Reference subjects provided by THOMAS
SUBJECTS = [el for el in os.listdir(PRIOR_PATH) if os.path.isdir(os.path.join(PRIOR_PATH, el)) and not el.startswith('.')]
assert len(SUBJECTS) > 0

# Names for command-line options and label filenmaes
ROI = {
    'param_all': 'ALL',  # special keyword to select all the rois
    'param_names': ('thalamus', 'av', 'va', 'vla', 'vlp', 'vpl', 'vl', 'pul', 'lgn', 'mgn', 'cm', 'md', 'hb', 'mtt','acc','cau','cla','gpe','gpi','put','rn','gp','amy'),
    'label_names': ('1-THALAMUS', '2-AV', '4-VA', '5-VLa', '6-VLP', '7-VPL', '4567-VL', '8-Pul', '9-LGN', '10-MGN', '11-CM', '12-MD-Pf', '13-Hb', '14-MTT', '26-Acc', '27-Cau', '28-Cla', '29-GPe', '30-GPi', '31-Put', '32-RN', '33-GP', '34-Amy'),
    }
ROI_CHOICES = (ROI['param_all'],)+ROI['param_names']

# Optimized hyper-parameters for PICSL
#db = shelve.open(os.path.join(RES_PATH, 'cv_optimal_picsl_parameters.shelve'), flag='r')
#OPTIMAL = dict(db)
#db.close()
OPTIMAL = dict()
OPTIMAL = {'PICSL': {'5-VLa': {'beta': 0.5, 'score': 0.61647925000000003, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '2-AV': {'beta': 1.0, 'score': 0.75553215624999992, 'rp': [2.0, 2.0, 2.0], 'rs': [4.0, 4.0, 4.0]},
                     '14-MTT': {'beta': 1.0, 'score': 0.64393765624999999, 'rp': [2.0, 2.0, 2.0], 'rs': [1.0, 1.0, 1.0]},
                     '10-MGN': {'beta': 5.0, 'score': 0.63739243749999996, 'rp': [3.0, 3.0, 3.0], 'rs': [2.0, 2.0, 2.0]},
                     '7-VPL': {'beta': 0.5, 'score': 0.61675868749999996, 'rp': [5.0, 5.0, 5.0], 'rs': [2.0, 2.0, 2.0]},
                     '4567-VL': {'beta': 2.0, 'score': 0.80880984374999998, 'rp': [3.0, 3.0, 3.0], 'rs': [2.0, 2.0, 2.0]},
                     '4-VA': {'beta': 0.5, 'score': 0.64682046874999999, 'rp': [5.0, 5.0, 5.0], 'rs': [0.0, 0.0, 0.0]},
                     '6-VLP': {'beta': 1.0, 'score': 0.69648359375000002, 'rp': [5.0, 5.0, 5.0], 'rs': [2.0, 2.0, 2.0]},
                     '11-CM': {'beta': 0.10000000000000001, 'score': 0.65230337500000002, 'rp': [2.0, 2.0, 2.0], 'rs': [1.0, 1.0, 1.0]},
                     '1-THALAMUS': {'beta': 1.0, 'score': 0.90461968749999999, 'rp': [2.0, 2.0, 2.0], 'rs': [4.0, 4.0, 4.0]},
                     '12-MD-Pf': {'beta': 2.0, 'score': 0.81991278125, 'rp': [2.0, 2.0, 2.0], 'rs': [2.0, 2.0, 2.0]},
                     '8-Pul': {'beta': 0.5, 'score': 0.83126987500000005, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '9-LGN': {'beta': 0.5, 'score': 0.66429712500000004, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '13-Hb': {'beta': 0.5, 'score': 0.63729618750000006, 'rp': [1.0, 1.0, 1.0], 'rs': [5.0, 5.0, 5.0]},
                     '26-Acc': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '27-Cau': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '28-Cla': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '29-GPe': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '30-GPi': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '31-Put': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '32-RN': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '33-GP': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]},
                     '34-Amy': {'beta': 2.0, 'score': 0.7, 'rp': [2.0, 2.0, 2.0], 'rs': [3.0, 3.0, 3.0]}
                     }}



if __name__ == '__main__':
    print(f"THOMAS_HOME={THOMAS_HOME}")
    print(f"SUBJECTS={SUBJECTS}")
    print(f"OPTIMAL={OPTIMAL}")
