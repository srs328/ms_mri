import os
import sys
#import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import re
import subprocess
import gzip

from libraries.parallel import command


def backup_file(input_image, output_image, command=os.system):
    """
    makes a backup of the input file to output specificed
    """
    command('cp %s %s' % (input_image, output_image))
    return output_image


def check_warps(warp_path):
    """
    Checks if the necessary ANTS warps exist.
    """
    warp_file = os.path.join(warp_path+'InverseWarp.nii.gz')
    affine_file = os.path.join(warp_path+'Affine.txt')
    if os.path.exists(warp_file) and os.path.exists(affine_file):
        return True
    return False


def create_atlas(label, path, subjects, target, output_atlas, debug=False):
    # Create 4D atlas for a label previously registered to a target subject
    label_paths = [os.path.join(path, subj, target, label+'.nii.gz') for subj in subjects]
    cmd = 'fslmerge -t %s %s' % (output_atlas, ' '.join(label_paths))
    command(cmd, debug=debug)
    return output_atlas, cmd


def flip_lr(input_image, output_image, command=os.system):
    command('fslswapdim %s -x y z %s' % (input_image, output_image))
    return output_image


def sanitize_input(input_image, output_image, command=os.system):
    """
    Standardizes the input to neurological coordinates and can flip to segment
    right thalamus.
    """
    command('fslreorient2std %s %s' % (input_image, output_image))
    return output_image


def sanitize_label_image(input_image, output_image, **exec_options):
    # Slicer puts data in LR convention for some reason
    cmd = 'fslswapdim %s LR PA IS %s; ' % (input_image, output_image)
    # Sometimes values are > 1
    cmd += 'fslmaths %s -bin %s' % (output_image, output_image)
    command(cmd, **exec_options)
    return output_image, cmd


def label_fusion_steps(input_image, image_atlas, label_atlas, output_label, sigma, X, mrf=0., debug=False):
    # Perform steps label fusion.  Parameter naming comes from Cardoso et al. 2013
    # verbose and only consider non-consensus voxels.
    cmd = 'seg_LabFusion -v -unc -in %s -STEPS %s %s %s %s -out %s' % (label_atlas, sigma, X, input_image, image_atlas, output_label)
    if 0 < mrf <= 5:
        cmd += ' -MRF_beta %g' % mrf
    command(cmd, debug=debug)
    return output_label, cmd


def label_fusion_picsl(input_image, atlas_images, atlas_labels, output_label, rp=[2, 2, 2], rs=[3, 3, 3], alpha=0.1, beta=2, **exec_options):
    """
    H Wang. Multi-Atlas Sementation with Joint Label Fusion. 2013.
    Joint Label Fusion:
    usage:
     jointfusion dim mod [options] output_image
    required options:
      dim                             Image dimension (2 or 3)
      mod                             Number of modalities or features
      -g atlas1_mod1.nii atlas1_mod2.nii ...atlasN_mod1.nii atlasN_mod2.nii ...
                                      Warped atlas images
      -tg target_mod1.nii ... target_modN.nii
                                      Target image(s)
      -l label1.nii ... labelN.nii    Warped atlas segmentation
      -m <method> [parameters]        Select voting method. Options: Joint (Joint Label Fusion)
                                      May be followed by optional parameters in brackets, e.g., -m Joint[0.1,2].
                                      See below for parameters
    other options:
      -rp radius                      Patch radius for similarity measures, scalar or vector (AxBxC)
                                      Default: 2x2x2
      -rs radius                      Local search radius.
                                      Default: 3x3x3
      -x label image.nii              Specify an exclusion region for the given label.
      -p filenamePattern              Save the posterior maps (probability that each voxel belongs to each label) as images.
                                      The number of images saved equals the number of labels.
                                      The filename pattern must be in C printf format, e.g. posterior%04d.nii.gz
    Parameters for -m Joint option:
      alpha                           Regularization term added to matrix Mx for inverse
                                      Default: 0.1
      beta                            Exponent for mapping intensity difference to joint error
                                      Default: 2
    """
    dim = 3
    mod = 1
    g = ' '.join(atlas_images)
    tg = input_image
    l = ' '.join(atlas_labels)
    m = 'Joint[%g,%g]' % (alpha, beta)
    rp = '%dx%dx%d' % tuple(rp)
    rs = '%dx%dx%d' % tuple(rs)
    cmd = 'jointfusion %s %s -g %s -tg %s -l %s -m %s -rp %s -rs %s %s' % (dim, mod, g, tg, l, m, rp, rs, output_label)
    command(cmd, **exec_options)
    return output_label, cmd


def label_fusion_picsl_ants(input_image, atlas_images, atlas_labels, output_label, rp=[2, 2, 2], rs=[3, 3, 3], alpha=0.1, beta=2, mask='', **exec_options):
    """
    COMMAND:
         antsJointFusion
              antsJointFusion is an image fusion algorithm developed by Hongzhi Wang and Paul
              Yushkevich which won segmentation challenges at MICCAI 2012 and MICCAI 2013. The
              original label fusion framework was extended to accommodate intensities by Brian
              Avants. This implementation is based on Paul's original ITK-style implementation
              and Brian's ANTsR implementation. References include 1) H. Wang, J. W. Suh, S.
              Das, J. Pluta, C. Craige, P. Yushkevich, Multi-atlas segmentation with joint
              label fusion IEEE Trans. on Pattern Analysis and Machine Intelligence, 35(3),
              611-623, 2013. and 2) H. Wang and P. A. Yushkevich, Multi-atlas segmentation
              with joint label fusion and corrective learning--an open source implementation,
              Front. Neuroinform., 2013.
    OPTIONS:
         -d, --image-dimensionality 2/3/4
              This option forces the image to be treated as a specified-dimensional image. If
              not specified, the program tries to infer the dimensionality from the input
              image.
         -t, --target-image targetImage
                            [targetImageModality0,targetImageModality1,...,targetImageModalityN]
              The target image (or multimodal target images) assumed to be aligned to a common
              image domain.
         -g, --atlas-image atlasImage
                           [atlasImageModality0,atlasImageModality1,...,atlasImageModalityN]
              The atlas image (or multimodal atlas images) assumed to be aligned to a common
              image domain.
         -l, --atlas-segmentation atlasSegmentation
              The atlas segmentation images. For performing label fusion the number of
              specified segmentations should be identical to the number of atlas image sets.
         -a, --alpha 0.1
              Regularization term added to matrix Mx for calculating the inverse. Default =
              0.1
         -b, --beta 2.0
              Exponent for mapping intensity difference to the joint error. Default = 2.0
         -r, --retain-label-posterior-images (0)/1
              Retain label posterior probability images. Requires atlas segmentations to be
              specified. Default = false
         -f, --retain-atlas-voting-images (0)/1
              Retain atlas voting images. Default = false
         -c, --constrain-nonnegative (0)/1
              Constrain solution to non-negative weights.
         -p, --patch-radius 2
                            2x2x2
              Patch radius for similarity measures. Default = 2x2x2
         -m, --patch-metric (PC)/MSQ
              Metric to be used in determining the most similar neighborhood patch. Options
              include Pearson's correlation (PC) and mean squares (MSQ). Default = PC (Pearson
              correlation).
         -s, --search-radius 3
                             3x3x3
                             searchRadiusMap.nii.gz
              Search radius for similarity measures. Default = 3x3x3. One can also specify an
              image where the value at the voxel specifies the isotropic search radius at that
              voxel.
         -e, --exclusion-image label[exclusionImage]
              Specify an exclusion region for the given label.
         -x, --mask-image maskImageFilename
              If a mask image is specified, fusion is only performed in the mask region.
         -o, --output labelFusionImage
                      intensityFusionImageFileNameFormat
                      [labelFusionImage,intensityFusionImageFileNameFormat,<labelPosteriorProbabilityImageFileNameFormat>,<atlasVotingWeightImageFileNameFormat>]
              The output is the intensity and/or label fusion image. Additional optional
              outputs include the label posterior probability images and the atlas voting
              weight images.
         --version
              Get version information.
         -v, --verbose (0)/1
              Verbose output.
         -h
              Print the help menu (short version).
         --help
              Print the help menu.
    """
    dim = 3
    g = ' '.join(atlas_images)
    tg = input_image
    l = ' '.join(atlas_labels)
    rp = 'x'.join(['%d' % el for el in rp])
    rs = 'x'.join(['%d' % el for el in rs])
    if mask:
        mask = '-x '+mask
    cmd = 'antsJointFusion -d %s -g %s -t %s -l %s -a %g -b %g -p %s -s %s %s -o %s' % (dim, g, tg, l, alpha, beta, rp, rs, mask, output_label)
    command(cmd, **exec_options)
    return output_label, cmd


def label_fusion_majority(atlas_labels, output_label, execute=command, **exec_options):
    cmd = 'ImageMath 3 %s MajorityVoting %s' % (output_label, ' '.join(atlas_labels))
    execute(cmd, **exec_options)
    return output_label, cmd


def read_ordering(afile):
    sp = subprocess.Popen('fslhd %s' % afile, stdout=subprocess.PIPE, shell=True)
    hdr = sp.communicate()[0].decode().split("\n")
    order = [el.split()[-1] for el in hdr if 'qform' in el and 'orient' in el]
    order = [''.join([e[0] for e in el.split('-to-')]) for el in order]
    return order


def closest_voxel_value(num, hist, ndx_maxy):
    """
    Get the highest closest voxel value from a specified number using the plot of the input image
    """
    curr = [30000]
    hist = list(hist)
    for i in range(ndx_maxy, len(hist)):
        if abs(num - hist[i]) < abs(num - curr[0]):
            curr[0] = hist[i]
    return curr[0]


def remap_image(input_image, output_image, order=3, contrast_stretching=1, scaling='WM'):
    # Default order is set to use a cubic function
    # Default scaling == "WM" (rescale using WM), specify a fix value, "T1" .
    input = nib.load(input_image)
    crop_data = input.get_fdata()
    hist, bin_edges = np.histogram(crop_data[crop_data != 0], bins="auto")
    #plt.hist(crop_data[crop_data != 0],bins="auto")

    # Find the voxel value shared by at least 1% of voxels mode
    # (i.e., the highest WM value avoiding outliers)
    maxy = hist.max()                # get the mode
    # get the index of the mode:
    imaxy = int((np.where(hist == maxy))[0])
    num = 0.01 * maxy                # 1%

    fin = closest_voxel_value(num, hist, imaxy)
    inum = np.where(hist == fin)[0]
    # in case of two identical values in the histogram (both sides of the histogram) then we want the one with the higher value.
    inum2 = int(inum[-1])
    reversalnum = bin_edges[inum2]
    reversalnum = reversalnum.tolist()
    crop_data_normwmn = crop_data / reversalnum   # normalize by WM

    if order > 4 or order < 0:
        print("ERROR: please enter an order between 1 and 4")
        sys.exit()
    elif order == 0:
        print("Order: ", order)
        crop_normwmn_rev = crop_data_normwmn   # no reversal
    elif order == 1:
        print("Order: ", order)
        crop_normwmn_rev = abs(1 - crop_data_normwmn)  # reverse the image linearly
    elif order == 2:
        print("Order: ", order)
        crop_normwmn_rev = abs(1+(0.4004*crop_data_normwmn)+(-1.3912*(crop_data_normwmn**2)))   # reverse the image using a quadratic function
    elif order == 3:
        print("Order: ", order)
        crop_normwmn_rev = abs(1+(0.597*crop_data_normwmn)+(-2.0067*(crop_data_normwmn**2))+(0.4529*(crop_data_normwmn**3)))   # reverse using a cubic function
    elif order == 4:
        print("Order: ", order)
        crop_normwmn_rev = abs(1+(0.0436*crop_data_normwmn)+(1.1467*(crop_data_normwmn**2))+(-4.9716*(crop_data_normwmn**3))+(2.9014*(crop_data_normwmn**4)))   # reverse using a quartic function

    if contrast_stretching == 1:
        print("contrast_stretching")
        p2 = np.percentile(crop_normwmn_rev, 2)
        p98 = np.percentile(crop_normwmn_rev, 98)
        #FINAL = exposure.rescale_intensity(crop_normwmn_rev, in_range=(p2, p98))  # contrast stretching
        FINAL = np.clip(crop_normwmn_rev, p2, p98)   # contrast stretching
        fmin = np.min(FINAL)
        fmax = np.max(FINAL)
        FINAL = (FINAL - fmin) / (fmax - fmin)
    else:
        FINAL = crop_normwmn_rev

    if scaling == "T1" :    # rescale to max of T1 input image
        max = np.max(crop_data)
    elif scaling == "WM":   # rescale to 99% end of WM peak (0.01 of WM mode) previously computed
        max = int(reversalnum)
    else:
        max = int(scaling)  # rescale using a user-specified value

    FINAL_rescale = FINAL * max
    print('Rescaling to ', np.max(FINAL_rescale))

    FIN = nib.Nifti1Image(FINAL_rescale, input.affine, input.header)
    FIN.header['cal_max'] = max   # modify the max value of the header using specified max
    nib.save(FIN, output_image)


def swapdimlike(input_image, like_image, output_image):
    "Swaps dimension ordering (reslices) of input image to match another."
    order = read_ordering(like_image)
    os.system(f"fslswapdim {input_image} {' '.join(order)} {output_image}")


def uncrop_by_mask(input_image, output_image, full_mask, padding=0, canvas=None, log_file=None):
    """
    Uncrop an image. Undoes ExtractRegionFromImageByMask.
    - log_file can be output from ExtractRegionFromImageByMask, otherwise it should be a mask image
    and the output will be generated by re-running ExtractRegionFromImageByMask.  padding is only relevant in the latter case.
    - canvas can be an image to paste the input into, otherwise it's blank 0s.
    """
    if (log_file is None):
        # Need to discover the bounding box: rerun ExtractRegionFromImageByMask
        cmd = f'ExtractRegionFromImageByMask 3 {full_mask} {output_image} {full_mask} 1 {padding}'
        log = os.popen(cmd).read()
    else:
        # The log file output by ExtractRegionFromImageByMask is given, so read it
        with open(log_file, 'r') as logfile:
            log = logfile.read()
    log = log.split('final cropped region')[-1]
    crop_index = re.search(r'Index:\s+\[(.*?)\]', log).group(1).replace(', ', 'x')
    if canvas is None:
        canvas = output_image
        cmd = f'CreateImage 3 {full_mask} {canvas} 0'
        os.system(cmd)
    cmd = f'PasteImageIntoImage 3 {canvas} {input_image} {output_image} {crop_index} -1 1'
    os.system(cmd)


def validate_nifti_file(input_image):
    """
    Peek into the given image file header to validate that it is a NIfTI file.
    Returns True or False.
    """
    if (input_image.endswith('.nii.gz')):
        with gzip.open(input_image, "rb") as gnii:
            header = gnii.peek(348)
            magic = header[344:347]
            return (magic == b'n+1')
    elif (input_image.endswith('.nii')):
        with open(input_image, "rb") as nii:
            header = nii.read(348)
            magic = header[344:347]
            return (magic == b'n+1')
    else:
        return False
