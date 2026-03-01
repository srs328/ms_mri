import os
import sys
#import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import re
import subprocess
import gzip

from libraries.parallel import command


def skull_strip(
    input_image: str,
    output_root: str = None,
    border: int = 0,
    csf: bool = True,
    **exec_options,
) -> tuple[str]:
    if output_root is None:
        output_root = os.path.dirname(input_image)
    basename = os.path.basename(input_image).removesuffix(".nii.gz")
    input_brain = os.path.join(output_root, f"{basename}_brain.nii.gz")
    input_mask = os.path.join(output_root, f"{basename}_mask.nii.gz")

    border_option = f" -b {border} "
    if csf is False:
        csf_option = " --no-csf "
    else:
        csf_option = ""
    cmd = f"mri_synthstrip -i {input_image} -o {input_brain} -m {input_mask}" + \
        border_option + csf_option
    
    exit_code = command(cmd, **exec_options)
    if exit_code > 0:
        raise Exception(f"mri_synthstrip failed for {input_image}")
    
    return (input_image, input_brain, input_mask)



def backup_file(input_image, output_image, command=os.system):
    """
    makes a backup of the input file to output specificed
    """
    command('cp %s %s' % (input_image, output_image))
    return output_image


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


def remap_image(input_image, output_image, crop_mask_image=None, order=3, contrast_stretching=1, scaling='WM'):
    # Default order is set to use a cubic function
    # Default scaling == "WM" (rescale using WM), specify a fix value, "T1" .
    input = nib.load(input_image)
    input_data = input.get_fdata()

    if crop_mask_image is not None:
        crop = nib.load(crop_mask_image)
        mask = crop.get_fdata()
    else:
        mask = input_data

    # use crop here
    # SRS-make the histogram only from values in the input image that are within the crop mask
    hist, bin_edges = np.histogram(input_data[mask != 0], bins="auto")
    #plt.hist(crop_data[crop_data != 0],bins="auto")

    # Find the voxel value shared by at least 1% of voxels mode
    # (i.e., the highest WM value avoiding outliers)
    maxy = hist.max()                # get the mode
    # get the index of the mode:
    imaxy = int((np.where(hist == maxy))[0][0])
    num = 0.01 * maxy                # 1%

    fin = closest_voxel_value(num, hist, imaxy)
    inum = np.where(hist == fin)[0]
    # in case of two identical values in the histogram (both sides of the histogram) then we want the one with the higher value.
    inum2 = int(inum[-1])
    reversalnum = bin_edges[inum2]
    reversalnum = reversalnum.tolist()

    # dont use crop here
    input_data_normwmn = input_data / reversalnum   # normalize by WM

    if order > 4 or order < 0:
        print("ERROR: please enter an order between 1 and 4")
        sys.exit()
    elif order == 0:
        print("Order: ", order)
        input_normwmn_rev = input_data_normwmn   # no reversal
    elif order == 1:
        print("Order: ", order)
        input_normwmn_rev = abs(1 - input_data_normwmn)  # reverse the image linearly
    elif order == 2:
        print("Order: ", order)
        input_normwmn_rev = abs(1+(0.4004*input_data_normwmn)+(-1.3912*(input_data_normwmn**2)))   # reverse the image using a quadratic function
    elif order == 3:
        print("Order: ", order)
        input_normwmn_rev = abs(1+(0.597*input_data_normwmn)+(-2.0067*(input_data_normwmn**2))+(0.4529*(input_data_normwmn**3)))   # reverse using a cubic function
    elif order == 4:
        print("Order: ", order)
        input_normwmn_rev = abs(1+(0.0436*input_data_normwmn)+(1.1467*(input_data_normwmn**2))+(-4.9716*(input_data_normwmn**3))+(2.9014*(input_data_normwmn**4)))   # reverse using a quartic function

    if contrast_stretching == 1:
        print("contrast_stretching")
        # mask input_normwmn_rev for percentiles
        p2 = np.percentile(input_normwmn_rev[mask != 0], 2)
        p98 = np.percentile(input_normwmn_rev[mask != 0], 98)
        #FINAL = exposure.rescale_intensity(crop_normwmn_rev, in_range=(p2, p98))  # contrast stretching
        FINAL = np.clip(input_normwmn_rev, p2, p98)   # contrast stretching
        fmin = np.min(FINAL)
        fmax = np.max(FINAL)
        FINAL = (FINAL - fmin) / (fmax - fmin)
    else:
        FINAL = input_normwmn_rev

    if scaling == "T1" :    # rescale to max of T1 input image
        max = np.max(input_data[mask != 0]) #! use crop here
    elif scaling == "WM":   # rescale to 99% end of WM peak (0.01 of WM mode) previously computed
        max = int(reversalnum)
    else:
        max = int(scaling)  # rescale using a user-specified value

    FINAL_rescale = FINAL * max
    print('Rescaling to ', np.max(FINAL_rescale))

    FIN = nib.Nifti1Image(FINAL_rescale, input.affine, input.header)
    FIN.header['cal_max'] = max   # modify the max value of the header using specified max
    nib.save(FIN, output_image)
    return output_image


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
