import os
import sys
import numpy as np
import nibabel
import tempfile
from pathlib import Path

from libraries.ants_tools import (
    ants_ApplyInvTransforms,
    ants_new_rigid_registration,
    bias_correct,
)

from libraries.imgtools import remap_image, skull_strip
from constants import ORIG_TEMPLATE, MASK_93B
from libraries.parallel import command

# figure out who will pass arguments like do_command and whether to switch to argparse
def create_wmn_image(
    input_image, work_dir=None, skip_long=True, **exec_options
):
    if work_dir is None:
        work_dir = os.path.join(os.path.dirname(input_image), "long_thomas_proc")
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
    os.chdir(work_dir)

    basename = os.path.basename(input_image).removesuffix(".nii.gz")

    template_mask = MASK_93B

    # will be produced by next steps
    input_cropmask = os.path.join(
        work_dir, basename + "_cropmask.nii.gz"
    )
    if not os.path.exists(input_cropmask) or not skip_long:
        # produces rigid0GenericAffine.mat
        print("Starting rigid affine registration of input and full template")
        _, output_rigid, cmd = ants_new_rigid_registration(
            ORIG_TEMPLATE, input_image, suppress=True
        )
        print(cmd)
        print(f"Produced {output_rigid}")

        # bring the template mask into the space of the input_image
        print(f"Inverse transforming {template_mask} to subject space")
        input_cropmask, cmd = ants_ApplyInvTransforms(
            template_mask, input_image, input_cropmask, **exec_options
        )  # produces input_cropmask
        print(cmd)
        print(f"Produced {input_cropmask}")

        # correction to match mask input to input image sform.
        command(f'fslcpgeom {input_image} {input_cropmask}')
    else:
        print(f"Crop mask already exists at {input_cropmask}")

    # skull strip and produce a brain mask
    print("Starting mri_synthstrip")
    input_image, input_brain, input_brainmask = skull_strip(
        input_image, border=0, suppress=True
    )
    print(f"mri_synthstrip produced {input_brain} and {input_brainmask}")

    print("Starting N4 bias correction")
    bias_correct(input_brain, input_brain, **exec_options)

    input_brain_wmn = os.path.join(
        os.path.dirname(input_brain), basename + "_brain_wmn.nii.gz"
    )
    input_brain_wmn = remap_image(
        input_brain, input_brain_wmn, crop_mask_image=input_cropmask
    )
    command(f"fslmaths {input_brain_wmn} -mul {input_brainmask} {input_brain_wmn}")


if __name__ == "__main__":
    input_image = sys.argv[1]
    if len(sys.argv) > 2:
        work_dir = sys.argv[2]
    else:
        work_dir = os.path.dirname(input_image)
    create_wmn_image(input_image, work_dir=work_dir, skip_long=True)
