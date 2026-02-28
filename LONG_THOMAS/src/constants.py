#!/usr/bin/env python3
"""
Paths, names, optimized hyper-parameters, and other constants for THOMAS.
"""
import os
#import shelve

# Read the environment variable containing the application's root directory
LONG_THOMAS_HOME = os.getenv('LONG_THOMAS_HOME')
if (not (LONG_THOMAS_HOME and os.path.isdir(LONG_THOMAS_HOME))):
    print("The environment variable LONG_THOMAS_HOME must be set before this program is run.")
    exit(1)

# Set path variables for code and resources:
RES_PATH = os.path.join(LONG_THOMAS_HOME, 'resources')
# assert os.path.exists(RES_PATH)

ORIG_TEMPLATE = os.path.join(RES_PATH, 'origtemplate.nii.gz')
# assert os.path.exists(ORIG_TEMPLATE)

ORIG_TEMPLATE_MNI_STRIPPED = os.path.join(RES_PATH, 'origtemplate_mni_stripped.nii.gz')
# assert os.path.exists(ORIG_TEMPLATE_MNI_STRIPPED)

TEMPLATE_93B = os.path.join(RES_PATH, 'templ_113x207x88.nii.gz')
# assert os.path.exists(TEMPLATE_93B)

MASK_93B = os.path.join(RES_PATH, 'mask_templ_93x187x68_B.nii.gz')
# assert os.path.exists(MASK_93B)

# Amount of padding to add for (default) bigger crop
UNCROP_PADDING = 10


if __name__ == '__main__':
    print(f"LONG_THOMAS_HOME={LONG_THOMAS_HOME}")
