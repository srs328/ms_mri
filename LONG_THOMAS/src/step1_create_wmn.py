import os
import sys
import numpy as np
import nibabel
import tempfile
from pathlib import Path

from libraries.ants_tools import (
    ants_ApplyInvTransforms, ants_apply_only_warp, ants_new_compose_a_to_b,
    ants_mi_nonlinear_registration, ants_new_nonlinear_registration,
    ants_v0_nonlinear_registration, ants_new_rigid_registration,
    # ants_warp_inverse_transform,
    bias_correct, crop_by_mask_cmd, denoise_image
)

from libraries.imgtools import (
  check_warps, sanitize_input, backup_file, flip_lr,
  label_fusion_picsl_ants, label_fusion_picsl,
  label_fusion_majority, remap_image
)

from longitudinal_pipeline.custom_pipeline.constants import (
  PRIOR_PATH, ORIG_TEMPLATE, ORIG_TEMPLATE_MNI_STRIPPED, TEMPLATE_93, MASK_93,
  TEMPLATE_93B, MASK_93B, SUBJECTS, ROI, OPTIMAL, UNCROP_PADDING, WMN_BIAS_IMAGE
)

# arguments

work_dir = "/mnt/i/Data/srs-9/longitudinal/sub1003/20170329/test_thomas"
orig_input_image = "t1.nii.gz"