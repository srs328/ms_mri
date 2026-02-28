import os
import sys
import numpy as np
import nibabel
import tempfile
import time

from functools import partial
from datetime import timedelta

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

from THOMAS_constants import (
  PRIOR_PATH, ORIG_TEMPLATE, ORIG_TEMPLATE_MNI_STRIPPED, TEMPLATE_93, MASK_93,
  TEMPLATE_93B, MASK_93B, SUBJECTS, ROI, OPTIMAL, UNCROP_PADDING, WMN_BIAS_IMAGE
)


def conservative_mask(do_command, input_masks, output_path, dilation=0, fill=False):
    """
    Estimates a conservative maximum mask given a list of input masks.
    - for dilation > 0 and fill=True, each side is padded by dilation instead
    - fill will fill the bounding box of the mask producing a cube
    """
    # Maximum label fusion
    # Taken from cv_registration_method.ants_label_fusions
    # cmd = 'AverageImages 3 %s 0 %s' % (output_path, ' '.join(input_masks))
    # cmd = 'ThresholdImage 3 %s %s 0.01 1000' % (output_path, output_path)
    # cmd = 'fslmaths %s -bin %s' % (' -add '.join(input_masks), output_path)
    cmd = 'c3d %s -accum -max -endaccum -binarize -o %s' % (' '.join(input_masks), output_path)
    do_command(cmd)
    if fill:
        # get bounding box
        bbox = list(map(int, os.popen('fslstats %s -w' % output_path).read().strip().split()))
        padding = (-dilation, 2 * dilation) * 3  # min index, size change for 3 spatial dimensions
        if dilation > 0:
            # edit bounding box
            for i, inc in enumerate(padding):  # ignore time dimensions
                bbox[i] += inc
        roi = ' '.join(map(str, bbox))
        # fill bounding box
        cmd = 'fslmaths %s -add 1 -bin -roi %s %s' % (output_path, roi, output_path)
    elif dilation > 0:
        kernel = '%dx%dx%dvox' % (dilation, dilation, dilation)
        cmd = 'c3d %s -dilate 1 %s -o %s' % (output_path, kernel, output_path)
    do_command(cmd)
    return output_path


def make_temp_directory(args):
    if (args.tempdir):
        temp_path = args.tempdir
        if (not os.path.exists(temp_path)):
            print('Making %s' % os.path.abspath(temp_path))
            os.makedirs(temp_path)
    else:
        temp_path = tempfile.mkdtemp(dir=os.path.dirname(args.output_path))
    return temp_path


def split_by_axis(roi, first, second, split_axis=2):
    """
    Splits the given ROI into 2 halves along the given split_axis (0..2), placing each
    half into the corresponding zero arrays (first and second).
    """
    # Test for no ROI in this slice:
    nzcnt = np.count_nonzero(roi)
    if (nzcnt < 1):
      return

    # divide the bounding box for non-zero-voxels in half (in the split axis dimension)
    nonzeros = np.nonzero(roi)
    start, stop = nonzeros[split_axis].min(0), nonzeros[split_axis].max(0) + 1
    first_idx = slice(start, start + (stop - start) // 2, 1)
    second_idx = slice(start + (stop - start) // 2, stop, 1)

    # create slice arrays and replace the split axis subslice
    first_slice = [slice(None,None,None) for i in range(3)]
    second_slice = [slice(None,None,None) for i in range(3)]
    first_slice[split_axis] = first_idx
    second_slice[split_axis] = second_idx

    # copy the selected input image data from each half
    first[*first_slice] = roi[*first_slice]
    second[*second_slice] = roi[*second_slice]


# As of python3, we think that split_halves and get_bounding box no longer work
# but are never called through split_roi anyway.
def get_bounding_box(A):
    B = np.argwhere(A)
    start, stop = B.min(0), B.max(0) + 1
    return list(zip(start, stop))

def split_halves(roi, first, second, sl, axis, split_axis):
    # Test for no ROI in this slice:
    if (np.count_nonzero(roi) <= 1):
      return
    N = len(roi.shape)
    idx = [slice(sl, sl+1) if el is axis else slice(None) for el in range(N)]
    try:
        box = get_bounding_box(roi[idx])
    except (ValueError, IndexError) as ex:
        # No ROI in this slice
        return
    try:
        box[axis] = tuple(el+sl for el in box[axis])
    except TypeError:
        # Occurs for axis=None case
        pass
    first_idx = [slice(a, a + (b-a) // 2) if i is split_axis else slice(a, b) for i, (a, b) in enumerate(box)]
    second_idx = [slice(a + (b-a) // 2, b) if i is split_axis else slice(a, b) for i, (a, b) in enumerate(box)]
    # Try pasting in the original ROI to the half boxes
    try:
        first[first_idx] = roi[first_idx]
    except ValueError:
        # exception if half box is 0 along one dimension
        pass
    try:
        second[second_idx] = roi[second_idx]
    except ValueError:
        pass


def split_roi(roi, axis, split_axis):
    """
    Pages through the roi along axis and cuts each slice in half in the split_axis dimension.
    axis=None cuts the 3D bounding box in half.
    """
    first = np.zeros_like(roi)
    second = np.zeros_like(roi)
    if axis is None:
        split_by_axis(roi, first, second, split_axis)
    else:
        for sl in range(roi.shape[axis]):
            split_halves(roi, first, second, sl, axis, split_axis)
    return first, second


def warp_atlas_subject(subject, path, labels, input_image, input_transform_prefix, output_path, exec_options={}):
    """
    Warp a training set subject's labels to input_image.
    """
    a_transform_prefix = os.path.join(path, subject + '/WMnMPRAGE')
    subj_path = os.path.join(output_path, subject)
    try:
        os.mkdir(subj_path)
    except OSError:
        # Exists
        pass
    combined_warp = os.path.join(subj_path, 'Warp.nii.gz')
    if (not os.path.exists(combined_warp)):
        ants_new_compose_a_to_b(a_transform_prefix, input_image, input_transform_prefix, combined_warp, **exec_options)
    output_labels = {}
    # OPT parallelize, or merge parallelism with subject level
    for label in labels:
        label_fname = os.path.join(path, subject, 'sanitized_rois', label + '.nii.gz')
        warped_label = os.path.join(subj_path, label + '.nii.gz')
        switches = '--use-NN'
        if (not os.path.exists(warped_label)):
            ants_apply_only_warp(input_image, label_fname, combined_warp, warped_label, switches, **exec_options)
        output_labels[label] = warped_label
    # Warp anatomical WMnMPRAGE_bias_corr too
    # TODO merge this into previous for loop to be DRY?
    output_labels['WMnMPRAGE_bias_corr'] = output_image = os.path.join(subj_path, WMN_BIAS_IMAGE)
    if (not os.path.exists(output_labels['WMnMPRAGE_bias_corr'])):
        print(output_labels['WMnMPRAGE_bias_corr'])
        ants_apply_only_warp(input_image, os.path.join(path, subject, WMN_BIAS_IMAGE), combined_warp, output_image, '--use-BSpline', **exec_options)
    return output_labels


def run_thomas(args, do_command, temp_path, pool, **exec_options):
    if (args.verbose):
        print(f"(run_thomas): args={args}, cmd={do_command}, temp_path={temp_path}, e_opts={exec_options}")

    input_image = orig_input_image = args.input_image

    # special case: oldT1 argument causes mvOnly to be set
    if args.oldt1:
       args.mvOnly = True

    # Set up output path
    if args.output_path:
        output_path = args.output_path
    else:
        output_path = os.path.dirname(orig_input_image)

    # Set up the ROIs
    if ROI['param_all'] in args.roi_names:
        labels = list(ROI['label_names'])
    else:
        roi_dict = dict(list(zip(ROI['param_names'], ROI['label_names'])))
        labels = [roi_dict[el] for el in args.roi_names]

    # Set up the template
    mask = MASK_93      # default value of mask
    if args.algorithm == "v2":
        if args.template is not None and args.mask is not None:
            template = args.template
            mask = args.mask
            print("Custom template and mask")
        elif args.template is not None and args.mask is None:
            sys.exit("!!!!!!! Both template and mask need to be specified simultaneously and they need to be of the same size !!!!!!!")
        elif args.template is None and args.mask is not None:
            sys.exit("!!!!!!! Both template and mask need to be specified simultaneously and they need to be of the same size !!!!!!!")
        else:
            if args.smallCrop:
                template = TEMPLATE_93
                mask = MASK_93
                print("Algorithm is v2 small crop")
            else:
                # SRS-this is the default condition for me
                template = TEMPLATE_93B # templ_113x207x88.nii.gz
                mask = MASK_93B # mask_templ_93x187x68_B.nii.gz; despite name, dimensions are close to template_93B, possibly slightly larger
                print("Algorithm is v2")
    elif args.algorithm == "v1":
        sys.exit("!!!!!!! v1 algorithm not yet implemented !!!!!!!")
    elif args.algorithm == "v0":
        template = ORIG_TEMPLATE
        print("Template is origtemplate.nii.gz")
    else:
        sys.exit("!!!!!!! Algorithm incorrectly specified !!!!!!!")

    # print 'Template being used is'
    # print os.path.abspath(template)

    if args.warp:
        warp_path = args.warp
    else:
        # TODO remove this as the default behavior, instead do ANTS?
        _, tail = os.path.split(input_image)
        tail = tail.replace('.nii', '').replace('.gz', '') #split('.', 1)[0]
        warp_path = os.path.join(temp_path, tail)

    t = time.time()

    if args.algorithm == "v2":
        # Crop the input
        # Affine registering template to input
        # For brain extracted (skull stripped) data, use MNI template for better registration
        # For now link denoise mask with using MNI template for affine registration
        file_name = os.path.basename(orig_input_image)
        base_name = file_name.replace('.gz','').replace('.nii','')
        if not(args.useMask):
            # For skull stripped data mni template is better kludge combine with denoise masking
            if (args.denoisemask):
                print('Denoising input image for cropping step only with stripped template')
                dorig_input_image = os.path.join(os.path.dirname(orig_input_image), 'dn_'+base_name+'.nii.gz')
                denoise_image(orig_input_image, dorig_input_image)
                ants_new_rigid_registration(ORIG_TEMPLATE_MNI_STRIPPED, dorig_input_image)
            else:
                ants_new_rigid_registration(ORIG_TEMPLATE, orig_input_image)
                print("Completed a quick rigid affine registration of input and full template")
        else:
            print("Skipping affine registration and using existing mask for cropping")

        mask_input = os.path.join(os.path.dirname(orig_input_image), 'mask_inp.nii.gz')
        # Transform mask from template space to input space
        # reverse order for both linear and nonlinear
        ants_ApplyInvTransforms(mask, orig_input_image, mask_input)
        # ants_warp_inverse_transform(mask, mask_input, orig_input_image)
        print("Completed transforming the mask from template space to input space")

        # correction to match mask input to input image sform.
        do_command(f'fslcpgeom {orig_input_image} {mask_input}')

        input_image = os.path.join(os.path.dirname(orig_input_image), 'crop_'+base_name+'.nii.gz')
        # Crop input using this mask
        if (args.smallCrop):
            do_command(crop_by_mask_cmd(orig_input_image, input_image, mask_input))
        else:
            # Add extra padding for the default, generous crop
            do_command(crop_by_mask_cmd(orig_input_image, input_image, mask_input, 1, UNCROP_PADDING))

        print('Completed cropping the input. Elapsed: %s' % timedelta(seconds=time.time()-t))


    # FSL automatically converts .nii to .nii.gz
    # sanitized_image and input_image named crop_<basename>.nii.gz
    sanitized_image = os.path.join(temp_path, os.path.basename(input_image) + ('.gz' if input_image.endswith('.nii') else ''))
    print('--- Reorienting image. --- Elapsed: %s' % timedelta(seconds=time.time()-t))
    if (not os.path.exists(sanitized_image)):
        # input_image becomes sanitized_image after this step, and is used for the rest of the pipeline
        input_image = sanitize_input(input_image, sanitized_image, do_command)
        if args.right:
            print('--- Flipping along L-R. --- Elapsed: %s' % timedelta(seconds=time.time()-t))
            flip_lr(input_image, input_image, do_command)
        print('--- Correcting bias. --- Elapsed: %s' % timedelta(seconds=time.time()-t))
        bias_correct(input_image, input_image, **exec_options)
    else:
        print('Skipped, using %s' % sanitized_image)
        input_image = sanitized_image

    #backup crop_ file before contrast adjustment
    if args.contrastsynth:
        # default condition for my usage; contrast synthesis on cropped and bias_corrected input
        print('Backing input image')
        binput_image = os.path.join(os.path.dirname(orig_input_image), 'bcrop_'+base_name+'.nii.gz')
        bsanitized_image = os.path.join(temp_path, os.path.basename(binput_image) + ('.gz' if input_image.endswith('.nii') else ''))
        backup_file(input_image, bsanitized_image)
        print('Contrast adjusting cropped image cubic stretch')
        remap_image(input_image, input_image, 3, 1, "WM")
    # Exiting after cropping
    if args.cropOnly:
        print("Using -co flag and exiting after completing cropping.")
        sys.exit(0)

    print('--- Registering to mean brain template. --- Elapsed: %s' % timedelta(seconds=time.time()-t))
    if args.forcereg or not check_warps(warp_path):
        if args.warp:
            print('Saving output as %s' % warp_path)
        else:
            warp_path = os.path.join(temp_path, tail)
            print('Saving output to temporary path.')
        # ants_nonlinear_registration(template, input_image, warp_path, **exec_options)
        print('temppath %s warppath %s input_image %s' % (temp_path, warp_path, input_image))

        if args.algorithm == "v2":
            if (args.movingImageMask):
                print(f"Using '{args.movingImageMask}' as mask for the moving image.")
            if (args.fixedImageMask):
                print(f"Using '{args.fixedImageMask}' as mask for the fixed image.")

            # legacy code for old MV MI based non contrast synthesis for T1
            if (args.oldt1):
                ants_mi_nonlinear_registration(template, input_image, warp_path, **exec_options)
            else:
                ants_new_nonlinear_registration(template, input_image, warp_path, args.fixedImageMask, args.movingImageMask, **exec_options)
        else:
            ants_v0_nonlinear_registration(template, input_image, warp_path, **exec_options)
    else:
        print('Skipped, using %sInverseWarp.nii.gz and %sAffine.txt' % (warp_path, warp_path))

    print('--- Warping prior labels and images. --- Elapsed: %s' % timedelta(seconds=time.time() - t))
    # TODO should probably use output from warp_atlas_subject instead of hard coding paths in create_atlas
    warped_labels = pool.map(partial(
        warp_atlas_subject,
        path=PRIOR_PATH,
        # TODO cleanup this hack to always have whole thalamus so can estimate mask
        labels=set(labels + ['1-THALAMUS']),
        input_image=input_image,
        input_transform_prefix=warp_path,
        output_path=temp_path,
        exec_options=exec_options,
    ), SUBJECTS)
    warped_labels = {label: {subj: d[label] for subj, d in zip(SUBJECTS, warped_labels)} for label in warped_labels[0]}
    # # print '--- Forming subject-registered atlases. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    # atlases = pool.map(partial(create_atlas, path=temp_path, subjects=SUBJECTS, target='', debug=exec_options['debug']),
    # [{'label': label, 'output_atlas': os.path.join(temp_path, label+'_atlas.nii.gz')} for label in warped_labels])
    # atlases = dict(zip(warped_labels, zip(*atlases)[0]))
    # atlas_image = atlases['WMnMPRAGE_bias_corr']
    atlas_images = list(warped_labels['WMnMPRAGE_bias_corr'].values())

    # FIXME use whole-brain template registration optimized parameters instead, these are from crop pipeline
    optimal_picsl = OPTIMAL['PICSL']
    # for k, v in warped_labels.iteritems():
    #     print k, v
    # for label in labels:
    #     print optimal_picsl[label]
    print('--- Performing MV Label Fusion. --- Elapsed: %s' % timedelta(seconds=time.time() - t))
    pool.map(partial(label_fusion_majority),
                [dict(
                    atlas_labels=list(warped_labels[label].values()),
                    output_label=os.path.join(temp_path, 'm'+label + '.nii.gz'),
                    **exec_options
                ) for label in labels])

    if args.antsfusion:
        print('--- Performing Ants Joint Fusion. --- Elapsed: %s' % timedelta(seconds=time.time() - t))
        # Estimate mask to restrict computation
        mask = os.path.join(temp_path, 'mask.nii.gz')
        if (not os.path.exists(mask)):
            conservative_mask(do_command, list(warped_labels['1-THALAMUS'].values()), mask, UNCROP_PADDING)
        pool.map(partial(label_fusion_picsl_ants, input_image, atlas_images),
                 [dict(
                     atlas_labels=list(warped_labels[label].values()),
                     output_label=os.path.join(temp_path, label + '.nii.gz'),
                     rp=optimal_picsl[label]['rp'],
                     rs=optimal_picsl[label]['rs'],
                     beta=optimal_picsl[label]['beta'],
                     mask=mask,
                     **exec_options
                 ) for label in labels])
    elif (not args.mvOnly):
        print('--- Performing PICSL/MALF Joint Fusion. --- Elapsed: %s' % timedelta(seconds=time.time() - t))
        pool.map(partial(label_fusion_picsl, input_image, atlas_images),
                 [dict(
                     atlas_labels=list(warped_labels[label].values()),
                     output_label=os.path.join(temp_path, label + '.nii.gz'),
                     rp=optimal_picsl[label]['rp'],
                     rs=optimal_picsl[label]['rs'],
                     beta=optimal_picsl[label]['beta'],
                     **exec_options
                 ) for label in labels])

    files = [(os.path.join(temp_path, label + '.nii.gz'), os.path.join(output_path, label + '.nii.gz')) for label in labels]
    if args.right:
        pool.map(flip_lr, files)
        files = [(os.path.join(output_path, label + '.nii.gz'), os.path.join(output_path, label + '.nii.gz')) for label in labels]

    # Re-sort output to original ordering
    pool.map(do_command, [f"swapdimlike.py {in_file} {orig_input_image} {out_file}" for in_file, out_file in files] )

    # Do the majority voting files
    files = [(os.path.join(temp_path, 'm'+ label + '.nii.gz'), os.path.join(output_path, 'm'+ label + '.nii.gz')) for label in labels]
    if args.right:
        pool.map(flip_lr, files)
        files = [(os.path.join(output_path, 'm'+ label + '.nii.gz'), os.path.join(output_path, 'm'+ label + '.nii.gz')) for label in labels]

     # Re-sort output to original ordering
    pool.map(do_command, [f"swapdimlike.py {in_file} {orig_input_image} {out_file}" for in_file, out_file in files] )

    if (not args.mvOnly):
        # get the vlp file path for splitting
        vlp_file = os.path.join(output_path, '6-VLP.nii.gz')

        # Re-orient to standard space - LR PA IS format
        san_vlp_file = os.path.join(output_path, 'san_6-VLP.nii.gz')
        # input_image1 = sanitize_input(vlp_file, san_vlp_file, do_command)
        sanitize_input(vlp_file, san_vlp_file, do_command)

        # get the sanitized vlp for processing
        input_nii = nibabel.load(san_vlp_file)
        data = input_nii.get_fdata()
        hdr = input_nii.header
        affine = input_nii.affine

        # Coronal axis for RL PA IS orientation
        vlps = split_roi(data, None, 2)
        for fname, sub_vlp in zip(['6_VLPv.nii.gz', '6_VLPd.nii.gz'], vlps):
            output_nii = nibabel.Nifti1Image(sub_vlp, affine, hdr)
            output_nii.to_filename(os.path.join(output_path, fname))

    print('--- Finished --- Elapsed: %s' % timedelta(seconds=time.time() - t))
