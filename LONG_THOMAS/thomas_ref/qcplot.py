#!/usr/bin/env python3

import os, sys
import argparse
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import nilearn.plotting as plotting


def make_argument_parser(argv):
    "Create, initialize, and return the command line argument parser."
    prog_name=argv[0]
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"{prog_name}: Produce quality control plots for the HIPS-THOMAS processed image."
    )
    # parser.add_argument('input_image', help='Filename of or file path to input image')
    parser.add_argument('-c', '--crop', default=None, help='Path to crop_*.nii.gz file')
    parser.add_argument('-oc', '--ocrop', default=None, help='Path to ocrop_*.nii.gz file (T1s only)')
    parser.add_argument('-r', '--regn', default=None, help='Path to regn.nii.gz file')
    parser.add_argument('-st', '--stlabels', default='sthomas_LR_labels.nii.gz',
                        help='Name of nii.gz file containing stlabels [default: sthomas_LR_labels.nii.gz]')
    parser.add_argument('-t', '--title', default=None, help='Title string for figure')
    parser.add_argument('-o', '--outfile', default='sthomas_LR_labels',
                        help='Name for QC plot output file (without file extension) [default: sthomas_LR_labels')
    return parser


def main(argv=None):
    # the main method requires no argument vector so it can be called by setuptools
    if (argv is None):                   # if called by setuptools
        argv = sys.argv                  # then fetch the arguments from the system
    parser = make_argument_parser(argv)
    args = parser.parse_args()

    IS_T1 = False
    if (args.ocrop):
        IS_T1 = True

    cwd = os.getcwd()
    stlabels = os.path.join(cwd, args.stlabels)

    # loop over files in left directory, looking for any files not given as arguments
    left_dir = os.path.join(cwd, 'left')
    for entry in os.listdir(left_dir):
        if (entry.startswith('crop_')):
            crop = os.path.join(left_dir, entry) if (not args.crop) else args.crop
        if (entry.startswith('ocrop_')):
            ocrop = os.path.join(left_dir, entry) if (not args.ocrop) else args.ocrop
            IS_T1 = True
        if (entry.startswith('regn_L')):
            regn = os.path.join(left_dir, entry) if (not args.regn) else args.regn
            regn_title = 'left' if (not args.regn) else os.path.dirname(args.regn)

    crop_img = nib.load(r'{}'.format(crop))
    if IS_T1:
        orig_img = nib.load(r'{}'.format(ocrop))
    else:
        orig_img = nib.load(r'{}'.format(crop))
    regn_img = nib.load(r'{}'.format(regn))
    stlabels_img = nib.load(r'{}'.format(stlabels))

    # Create figure and allocate subplots
    fig0 = plt.figure(figsize=(12,8))
    gs = gridspec.GridSpec(3,1, wspace = 0)

    # Set titles for subplots
    if len(sys.argv) >= 4:
        plt.subplot(gs[0]).set_title(args.title, fontsize = 10)
    else:
        plt.subplot(gs[0]).set_title(cwd, fontsize = 10)

    if IS_T1:
        plt.subplot(gs[1]).set_title('THOMAS labels overlaid on HIPS T1', fontsize = 10)
    else:
        plt.subplot(gs[1]).set_title('THOMAS labels overlay', fontsize = 10)

    plt.subplot(gs[2]).set_title(f'{regn_title} regn edges overlay', fontsize = 10)

    # Fill in subplot 0: cut coordinates derived from hidden labels image, which is overlaid on original image
    display = plotting.plot_roi(stlabels_img, orig_img, alpha=0, linewidths=1, view_type="continuous", axes=plt.subplot(gs[0]), draw_cross=False)

    # Fill in subplot 1: overlay ROIs on basic crop image
    plotting.plot_anat(crop_img, axes=plt.subplot(gs[1]), draw_cross=False, cut_coords=(display.cut_coords[0], display.cut_coords[1], display.cut_coords[2]))
    plotting.plot_roi(stlabels_img, crop_img, linewidths=1, view_type="contours", axes=plt.subplot(gs[1]), draw_cross=False, cut_coords=(display.cut_coords[0], display.cut_coords[1], display.cut_coords[2]))

    # Fill in subplot 2: overlay regn edges on basic crop image
    edge_plot = plotting.plot_anat(crop_img, axes=plt.subplot(gs[2]), draw_cross=False, cut_coords=(display.cut_coords[0], display.cut_coords[1], display.cut_coords[2]))
    edge_plot.add_edges(regn_img)

    plt.savefig('{}'.format(args.outfile))



if __name__ == '__main__':
    main()
