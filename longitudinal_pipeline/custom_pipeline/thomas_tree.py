#!/usr/bin/env python3

import os
import sys
import argparse
from collections import namedtuple
from shutil import rmtree

from libraries.parallel import make_partial_command
from libraries.imgtools import validate_nifti_file


THOMAS_DIR_EXT = '.thomas'
IMAGE_EXTS = ['.nii', '.nii.gz']

Todo = namedtuple('Todo', 'fdir fname')

def find_candidate_images(root_dir):
    """
    Walk the given directory tree returning path and filename information for each
    input image file which does not appear to have been previously processed.
    The given root directory is assumed to exist.
    Returns a list of dictionaries of image file path information.
    """
    candidates = []
    for root, _, files in os.walk(root_dir, topdown=True):
        if (not root.endswith(THOMAS_DIR_EXT)):
            for fname in files:
                for ext in IMAGE_EXTS:
                    if (fname.endswith(ext)):
                        fbase = fname[:-(len(ext))]
                        fdir = os.path.join(root, fbase) + THOMAS_DIR_EXT
                        candidates.append({
                            'root': root, 'fname': fname, 'ext': ext,
                            'fbase': fbase, 'fdir': fdir,
                            'fpath': os.path.join(root, fname),
                            'flink': os.path.join(fdir, fname)
                        })
    return candidates


def handle_existing_results(candidates, args):
    """
    Use the status of the overwrite flag to remove or ignore existing THOMAS results directories.
    """
    selected = []
    for finfo in candidates:
        fdir = finfo['fdir']
        if (os.path.exists(fdir)):
            if (args.overwrite):            # if overwriting previous results
                rmtree(fdir)                # remove previous results
                selected.append(finfo)      # select image for processing
            else:
                print(f'WARNING: Directory "{fdir}" exists and overwrite argument not specified. Skipping...')
        else:
            selected.append(finfo)          # else, select image for processing
    return selected


def make_processing_infrastructure(selected, args):
    """
    Create a subdirectory containing a link to the image for each selected image to be processed.
    Returns a 'todo' list of two-tuples containing the directory and image name to process.
    """
    todo_list = []
    for finfo in selected:
        if (os.path.exists(finfo['fdir'])):         # should never happen because of prior filtering
            print(f"EXISTS! skipping {finfo['fdir']}")
        else:
            # print(f"mkdir: {finfo['fdir']}")
            os.mkdir(finfo['fdir'])
            # print(f" link: {finfo['fpath']}\n         {finfo['flink']}\n")
            os.link(finfo['fpath'], finfo['flink'])
            todo_list.append(Todo(finfo['fdir'], finfo['fname']))
    return todo_list


def run_thomases(todo_list, do_command, args):
    """
    Move through the filetree, calling the THOMAS Docker container on each linked image file
    within a newly created thomas subdirectory.
    """
    for todo in todo_list:
        print(f"Running THOMAS on '{todo.fname}' in directory '{todo.fdir}'...")
        verbose_arg = '-v' if args.verbose else ''
        t1_arg = '-t1' if (args.image_type.lower() == 't1') else ''
        cmd = f'hipsthomas.sh {verbose_arg} -i {todo.fname} {t1_arg}'
        os.chdir(todo.fdir)
        if (args.verbose):
            print(f"In directory '{os.getcwd()}' running command '{cmd}'")
        do_command(cmd)


def validate_nifti_files (candidates):
    """
    Return a list of input image file information for all files which have been
    validated as NIfTI files.
    """
    validated = []
    for candidate in candidates:
        if (not validate_nifti_file(candidate['fpath'])):
            print(f"ERROR: {candidate['fpath']} does not appear to be a valid NIfTI file. Skipping it...")
        else:
            validated.append(candidate)
    return validated


def make_argument_parser(argv):
    "Create, initialize, and return the command line argument parser."
    prog_name=argv[0]
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"{prog_name}: Run the THOMAS program to segment the thalamus on a given WMnMPRAGE or T1w image."
    )
    parser.add_argument('image_type', choices=['t1', 'T1', 'wmn', 'WMn', 'WMN'],
                        help='Type of image files in the given filetree (files MUST all be the same type)')
    parser.add_argument('-overwrite', '--overwrite', action='store_true',
                        help='Overwrite previous THOMAS results. WARNING: this will DELETE any previous THOMAS result directories in the filetree. [default: False]')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    return parser


def main(argv=None):
    # the main method requires no argument vector so it can be called by setuptools
    if (argv is None):                   # if called by setuptools
        argv = sys.argv                  # then fetch the arguments from the system
    parser = make_argument_parser(argv)
    args = parser.parse_args()

    exec_options = {'verbose': args.verbose}
    do_command = make_partial_command(**exec_options)

    validated = validate_nifti_files(find_candidate_images(os.getcwd()))
    selected = handle_existing_results(validated, args)
    todo_list = make_processing_infrastructure(selected, args)
    run_thomases(todo_list, do_command, args)



if __name__ == '__main__':
    main()
