#!/usr/bin/env python3
"""
Segment subject for selected thalamic nuclei using whole-brain registration via a template and PICSL label fusion.
"""
import os
import sys
import argparse

from shutil import rmtree

from libraries.parallel import (BetterPool, make_partial_command)
from libraries.run_thomas import make_temp_directory, run_thomas

from THOMAS_constants import ROI_CHOICES


def make_argument_parser(argv):
    "Create, initialize, and return the command line argument parser."
    prog_name=argv[0]
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"{prog_name}: Run the THOMAS program to segment the thalamus on a given WMnMPRAGE or T1w image."
    )
    parser.add_argument('input_image', help='input WMnMPRAGE NiFTI image, may need to be in "LR PA IS" format')
    parser.add_argument('roi_names', metavar='roi_names', choices=ROI_CHOICES, nargs='+', help='a space separated list of one or more ROIs. Valid targets are: %s' % ', '.join(ROI_CHOICES))
    parser.add_argument('-a', '--algorithm', type=str, required=True, help='version of THOMAS: v0 or v2')
    parser.add_argument('-c', '--contrastsynth', action='store_true', help='remap contrast for T1 inputs')
    parser.add_argument('-co', '--cropOnly', action='store_true', help='Stop after cropping')  # New argument for stopping after registration
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debug mode: forces serial processing, retains temp directories')
    parser.add_argument('-dm', '--denoisemask', action='store_true', help='denoise T1 input for mask comp')
    parser.add_argument('-F', '--forcereg', action='store_true', help='force ANTS registration to WMnMPRAGE mean brain template. The --warp argument can be then used to specify the output path.')
    parser.add_argument('-mvo', '--mvOnly', action='store_true', help='use only majority voting for joint fusion')
    parser.add_argument('--oldt1', action='store_true', help='old MI majority voting for T1 for legacy purposes')
    parser.add_argument('-p', '--processes', nargs='?', default=None, const=None, type=int, help='number of parallel processes to use.  If unspecified, automatically set to number of CPUs.')
    parser.add_argument('-R', '--right', action='store_true', help='segment right thalamus')
    parser.add_argument('-sc', '--smallCrop', action='store_true', help='Use a smaller cropping region than the default. WARNING: this will not produce reliable results for non-Thalamic structures.')
    parser.add_argument('-um', '--useMask', action='store_true', help='Use the provided mask to segment')  # New argument for custom crop mask
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('-xf', '--fixedImageMask', default=None, help='fixed image mask used for non-linear registration')
    parser.add_argument('-xm', '--movingImageMask', default=None, help='moving image mask used for non-linear registration')
    parser.add_argument('-w', '--warp', metavar='path', help='looks for {path}InverseWarp.nii.gz and {path}Affine.txt instead of basing it off input_image')
    parser.add_argument('--antsfusion', action='store_true', help='Use Ants joint fusion algorithm instead of PICSL/MALF joint fusion')
    parser.add_argument('--mask', help='custom mask if 93x187x68 mask size is not wanted')
    # parser.add_argument('--output_path', help='specify a path for the output file (for a single ROI) or to a directory for multiple ROIs')
    parser.add_argument('--output_path', help='specify a path to an output directory')
    parser.add_argument('--tempdir', help='temporary directory to save intermediate results (will not be deleted after a run)')
    parser.add_argument('--template', help='custom template if 93x187x68 size is not wanted')
    # TODO handle single ROI, single output file case
    # TODO go back to shell=False for command to suppress output and then fix sanitize labels
    return parser


def main(argv=None):
    # the main method requires no argument vector so it can be called by setuptools
    if (argv is None):                   # if called by setuptools
        argv = sys.argv                  # then fetch the arguments from the system
    parser = make_argument_parser(argv)
    args = parser.parse_args()

    exec_options = {'debug': args.debug, 'suppress': True}
    if args.verbose:
        exec_options['verbose'] = True
    if args.debug:
        print('Debugging mode forces serial execution.')
        args.processes = 1

    temp_path = make_temp_directory(args)

    do_command = make_partial_command(**exec_options)

    pool = BetterPool(args.processes)
    print('Running with %d processes.' % pool._processes)

    try:
        run_thomas(args, do_command, temp_path, pool, **exec_options)
    finally:
        pool.close()
        # Clean up temp folders
        if (not args.debug and not args.tempdir):
            try:
                rmtree(temp_path)
            except OSError as exc:
                if (exc.errno != 2):  # Code 2 - no such file or directory
                    raise



if __name__ == '__main__':
    main()
