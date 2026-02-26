import os
import sys
#import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import re
import subprocess
import gzip

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
    imaxy = int((np.where(hist == maxy))[0][0])
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
