import os
import sys
from libraries.parallel import command


def ants_nonlinear_registration(template, input_image, output, switches='', linear=False, cost='CC', **exec_options):
    """Do nonlinear registration with ANTS as in buildtemplateparallel.sh"""
    if linear:
        iterations = '0'
    else:
        iterations = '90x90x20'
    cmd = 'ANTS 3 -m %s[%s,%s,1,5] -v -t SyN[0.25] -r Gauss[3,0] -o %s -i %s --use-Histogram-Matching --number-of-affine-iterations 10000x10000x10000x10000x10000 --MI-option 32x16000 %s' % (cost, template, input_image, output, iterations, switches)
    output_warp = output+'Warp.nii.gz'
    output_affine = output+'Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_new_nonlinear_registration(template, input_image, output, fixedImageMask=None, movingImageMask=None, switches='', **exec_options):
    """Do nonlinear registration with antsRegistration"""
    print(f"(ants_new_nonlinear_registration): fixed={fixedImageMask}, moving={movingImageMask}")
    if (fixedImageMask and movingImageMask):
        xarg = f"-x [{fixedImageMask},{movingImageMask}]"
    elif (fixedImageMask):
        xarg = f"-x {fixedImageMask}"
    elif (movingImageMask):
        xarg = f"-x {movingImageMask}"
    else:
        xarg = ""
    cmd = f'antsRegistration -v -d 3 {xarg} --float 0 --output {output} --use-histogram-matching 1 -t Rigid[0.1] --metric Mattes[{template},{input_image},1,32,None] --convergence [500x500x500x500x500,1e-6,10] -f 5x5x5x5x4 -s 1.685x1.4771x1.256x1.0402x0.82235mm -r rigid0GenericAffine.mat -t Affine[0.1] --metric Mattes[{template},{input_image},1,64, None] --convergence [450x150x50,1e-7,10] -f 3x2x1 -s 0.60056x0.3677x0mm -t SyN[0.4,3.0] --metric CC[{template},{input_image},1,5] --convergence [200x200x90x50,1e-10,10] -f 4x3x2x1 -s 0.82x0.6x0.3677x0.0mm'
    output_warp = output+'Warp.nii.gz'
    output_affine = output+'Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_mi_nonlinear_registration(template, input_image, output, switches='', **exec_options):
    """Do nonlinear registration with antsRegistration MI syn """
    cmd = 'antsRegistration -v -d 3 --float 0 --output %s --use-histogram-matching 1 -t Rigid[0.1] --metric Mattes[%s,%s,1,32,None] --convergence [500x500x500x500x500,1e-6,10] -f 5x5x5x5x4 -s 1.685x1.4771x1.256x1.0402x0.82235mm -r rigid0GenericAffine.mat -t Affine[0.1] --metric Mattes[%s,%s,1,64, None] --convergence [450x150x50,1e-7,10] -f 3x2x1 -s 0.60056x0.3677x0mm -t SyN[0.4,3.0] --metric MI[%s,%s,1,32,None] --convergence [200x200x90x50,1e-10,10] -f 4x3x2x1 -s 0.82x0.6x0.3677x0.0mm' % (output, template, input_image, template, input_image, template, input_image)
    output_warp = output+'Warp.nii.gz'
    output_affine = output+'Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_v0_nonlinear_registration(template, input_image, output, switches='', **exec_options):
    """Do nonlinear registration with antsRegistration but no -r option """
    cmd = 'antsRegistration -d 3 --float 0 --output %s -t Affine[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100,1e-6,10] -f 8x4x2x1 -s 3x2x1x0vox -t SyN[0.1,3.0] --metric CC[%s,%s,1,4] --convergence [70x70x20,1e-6,10] -f 4x2x1 -s 2x1x0vox' % (output, template, input_image, template, input_image)
    output_warp = output+'Warp.nii.gz'
    output_affine = output+'Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_linear_registration(template, input_image, cost='CC', **exec_options):
    cmd = 'ANTS 3 -m %s[%s,%s,1,5] -o linear -i 0 --use-Histogram-Matching --number-of-affine-iterations 10000x10000x10000x10000x10000 --MI-option 32x16000 --rigid-affine true' % (cost, template, input_image)
    output_warp = 'linearWarp.nii.gz'
    output_affine = 'linearAffine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_oldrigid_registration(template, input_image, cost='CC', **exec_options):
    cmd = 'ANTS 3 -m %s[%s,%s,1,5] -o linear -i 0 --use-Histogram-Matching --number-of-affine-iterations 10000x10000x10000x10000x10000 --MI-option 32x16000 --rigid-affine false' % (cost, template, input_image)
    output_warp = 'linearWarp.nii.gz'
    output_affine = 'linearAffine.txt'
    command(cmd, **exec_options)
    return output_warp, output_affine, cmd


def ants_rigid_registration(fixed, moving, cost='MI', **exec_options):
    cmd = 'antsRegistration -d 3 --float 0 --output rigid -t Rigid[0.1] -r [%s,%s,1]  --metric %s[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 1e-6,10] -v -f 8x4x2x1 -s 3x2x1x0vox' % (fixed, moving, cost, fixed, moving)
    output_warp = 'rigid.nii.gz'
    output_rigid = 'rigidGeneric0Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_rigid, cmd


def ants_new_rigid_registration(fixed, moving, work_dir=None, cost='MI', **exec_options):
    if work_dir is not None:
        os.chdir(work_dir)
    cmd = 'antsRegistration -d 3 --float 0 --output rigid --interpolation Linear --use-histogram-matching 0 --winsorize-image-intensities [ 0.005,0.995 ] -r [%s,%s,1] -t Rigid[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 7e-7,10] -v -f 12x8x4x2 -s 4x3x2x1vox -t Affine[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 4e-7,10] -v -f 12x8x4x2 -s 4x3x2x1vox  ' % (fixed, moving, fixed, moving, fixed, moving)
    #cmd = 'antsRegistration -d 3 --float 0 --output rigid --interpolation Linear --use-histogram-matching 0 --winsorize-image-intensities [ 0.005,0.995 ] -r [%s,%s,1] -t Rigid[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 5e-7,10] -v -f 8x4x2x1 -s 3x2x1x0vox -t Affine[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 5e-7,10] -v -f 8x4x2x1 -s 3x2x1x0vox  ' % (fixed, moving, fixed, moving, fixed, moving)
    #cmd = 'antsRegistration -d 3 --float 0 --output rigid -t Rigid[0.1] -r [%s,%s,1]  --metric %s[%s,%s,1,32,None] --convergence [1000x500x250x100, 1e-6,10] -v -f 8x4x2x1 -s 3x2x1x0vox' % (fixed, moving, cost, fixed, moving)
    output_warp = 'rigid.nii.gz'
    output_rigid = 'rigidGeneric0Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_rigid, cmd


def ants_apply_warp(template, input_image, input_warp, input_affine, output_image, switches='', ants_apply=False, **exec_options):
    if ants_apply:
        cmd = f"WarpImageMultiTransform.py {switches} {input_image} {output_image} {template} {input_warp} {input_affine}"
    else:
        cmd = f"WarpImageMultiTransform 3 {input_image} {output_image} {input_warp} {input_affine} -R {template} {switches}"
    command(cmd, **exec_options)
    return output_image, cmd


def ants_apply_only_warp(template, input_image, input_warp, output_image, switches='', **exec_options):
    cmd = 'WarpImageMultiTransform 3 %s %s %s -R %s %s' % (input_image, output_image, input_warp, template, switches)
    command(cmd, **exec_options)
    return output_image, cmd


def ants_warp_inverse_transform(input_image, output_image, template, **exec_options):
    cmd = 'WarpImageMultiTransform 3 %s %s -R %s -i linearAffine.txt' % (input_image, output_image, template)
    command(cmd, **exec_options)
    return output_image, cmd


def ants_compose_a_to_b(a_transform_prefix, b_path, b_transform_prefix, output, **exec_options):
    """
    Compose a to b via an intermediate template space
    """
    a_affine = a_transform_prefix+'Affine.txt'
    a_warp = a_transform_prefix+'Warp.nii.gz'

    b_affine = '-i '+b_transform_prefix+'Affine.txt'
    b_warp = b_transform_prefix+'InverseWarp.nii.gz'
    cmd = 'ComposeMultiTransform 3 %s %s %s %s %s -R %s' % (output, b_affine, b_warp, a_warp, a_affine, b_path)
    command(cmd, **exec_options)
    return output, cmd


def ants_new_compose_a_to_b(a_transform_prefix, b_path, b_transform_prefix, output, **exec_options):
    """
    Compose a to b via an intermediate template space
    """
    a_affine = a_transform_prefix+'Affine.txt'
    a_warp = a_transform_prefix+'Warp.nii.gz'

    b_affine = '-i '+b_transform_prefix+'0GenericAffine.mat'
    b_warp = b_transform_prefix+'1InverseWarp.nii.gz'
    cmd = 'ComposeMultiTransform 3 %s %s %s %s %s -R %s' % (output, b_affine, b_warp, a_warp, a_affine, b_path)
    command(cmd, **exec_options)
    return output, cmd


def ants_ApplyTransforms(input_image, reference, output_image, **exec_options):
    cmd = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t rigid0GenericAffine.mat' % (input_image, reference, output_image)
    command(cmd, **exec_options)
    return output_image, cmd


def ants_ApplyInvTransforms(input_image, reference, output_image, **exec_options):
    cmd = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t [rigid0GenericAffine.mat , 1]' % (input_image, reference, output_image)
    command(cmd, **exec_options)
    return output_image, cmd


def ants_label_fusions(output_prefix, labels, images=None):
    """
    Returns commands for various ANTS label fusion schemes.
    For correlation voting, the last element of images should be the target image to compare priors against.
    """
    l = ' '.join(labels)
    cmds = []
    outputs = []
    # Maximum
    output = output_prefix + '_maximum.nii.gz'
    cmd = 'AverageImages 3 %s 0 %s;' % (output, l)
    cmd += 'ThresholdImage 3 %s %s 0.01 1000' % (output, output)  # essentitally make 1 anything bigger than 9
    cmds.append(cmd)
    outputs.append(output)
    # Majority
    output = output_prefix + '_majority.nii.gz'
    cmd = 'ImageMath 3 %s MajorityVoting %s' % (output, l)
    cmds.append(cmd)
    outputs.append(output)
    # STAPLE
    output = output_prefix + '_staple.nii.gz'
    output_probability = output_prefix + '_staple0001.nii.gz'  # STAPLE outputs a probability map for each label
    confidence = 0.5
    cmd = 'ImageMath 3 %s STAPLE %s %s;' % (output, confidence, l)
    # Threshold at 0.5 even though this is known to be loose (Cardoso STEPS 2013), that's okay for this purpose
    cmd += 'ThresholdImage 3 %s %s 0.5 1000' % (output_probability, output)
    cmds.append(cmd)
    outputs.append(output)
    if images is not None:
        # Correlation Vote
        output = output_prefix + '_correlation.nii.gz'
        template = images.pop()
        cmd = 'ImageMath 3 %s CorrelationVoting %s %s %s' % (output, template, ' '.join(images), l)
        cmds.append(cmd)
        outputs.append(output)
    return outputs, cmds


def bias_correct(input_image, output_image, **exec_options):
    cmd = 'N4BiasFieldCorrection -d 3 -i %s -o %s -b [200] -s 3 -c [50x50x30x20,1e-6]' % (input_image, output_image)
    command(cmd, **exec_options)
    return output_image, cmd


def copy_header(reference, target, output, switches='1 1 1', debug=False):
    """
    Copies NIFTI header information from reference to target resulting in output.
    Usage:  CopyImageHeaderInformation refimage.ext imagetocopyrefimageinfoto.ext imageout.ext   boolcopydirection  boolcopyorigin boolcopyspacing  {bool-Image2-IsTensor}
    """
    cmd = 'CopyImageHeaderInformation %s %s %s %s' % (reference, target, output, switches)
    command(cmd, debug=debug)
    return output, cmd


def crop_by_mask_cmd(input_image, output_image, mask, label=1, padding=0):
    # ExtractRegionFromImageByMask ImageDimension inputImage outputImage labelMaskImage [label=1] [padRadius=0]
    cmd = 'ExtractRegionFromImageByMask 3 %s %s %s %s %s' % (input_image, output_image, mask, label, padding)
    return cmd


def crop_prior_using_transform(output, crop, mask, padding, prior, affine, prior_padding=0, includes=[], output_mask=None):
    """
    Takes a cropped box with the mask and padding amount that defined it and brings it to another space via an (inverse) affine transform.
    - includes is a list of label masks in the prior space that must be included in the cropped_prior, assumes label masks are 0/1
    """
    import random

    if output_mask is None:
        output_mask = output
    cmds = []
    # Make all 1s
    # CreateImage imageDimension referenceImage outputImage constant [random?]
    # Need to use a temporary file here beause uncrop.py overwrites with the empty output image at the first step
    # TODO use python temp file
    ones = output+'_DELETEME_%s.nii.gz' % str(random.random())[2:]
    cmds.append('CreateImage 3 %s %s 1' % (crop, ones))
    # Uncrop
    # uncrop.py input_image output_image full_mask <padding> <canvas_image>
    cmds.append('%s %s %s %s %s' % (os.path.join(sys.path[0], 'uncrop.py'), ones, output_mask, mask, padding))
    # Transform using inverse of provided affine
    # WarpImageMultiTransform ImageDimension moving_image output_image  -R reference_image --use-NN   SeriesOfTransformations
    cmds.append('WarpImageMultiTransform 3 %s %s -R %s --use-NN -i %s' % (output_mask, output_mask, prior, affine))
    # Incorporate must-include label masks, assumes label masks are 0/1, otherwise overadd will be problematic
    for include in includes:
        cmds.append('ImageMath 3 %s overadd %s %s' % (output_mask, output_mask, include))
    # Crop
    cmds.append(crop_by_mask_cmd(prior, output, output_mask, padding=prior_padding))
    cmds.append('rm %s' % ones)
    return '; '.join(cmds)


def denoise_image(input_image, output_image, command=os.system):
    """
    DenoiseImage the input file to output specificed
    """
    command('DenoiseImage -d 3 -i %s -n Rician -o %s' % (input_image, output_image))
    return output_image
