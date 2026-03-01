from pathlib import Path
from create_wmn import create_wmn_image
import sys
import argparse



def make_argument_parser(argv):
    "Create, initialize, and return the command line argument parser."
    prog_name=argv[0]
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"{prog_name}: Synthesize white matter null images for sessions of a subject"
    )
    parser.add_argument("dataroot", type=str, help="Location of subject roots")
    parser.add_argument("subid", type=int, help="Four digit subject ID")
    parser.add_argument("sessions", nargs="+", type=str, help="List of sessions to process")
    parser.add_argument("--work-dir", type=str, help="Location to save intermediary files")
    return parser


def main(argv=None):
    # the main method requires no argument vector so it can be called by setuptools
    if (argv is None):                   # if called by setuptools
        argv = sys.argv                  # then fetch the arguments from the system
    parser = make_argument_parser(argv)
    args = parser.parse_args()

    dataroot = Path(args.dataroot)
    subject_root = dataroot / f"sub{args.subid}"
    session_roots = [subject_root / sesid for sesid in args.sessions]
    print(subject_root, subject_root.exists())
    print(f"Beginning to process {args.subid}")
    for session_root in session_roots:
        print(f"Starting session {session_root.name}")
        input_t1 = session_root / "t1.nii.gz"
        create_wmn_image(input_t1, work_dir=args.work_dir)

if __name__ == '__main__':
    main()

    # step1_create_wmn $dataroot $subid 20170329 20180406 20191017 20200728 20210918