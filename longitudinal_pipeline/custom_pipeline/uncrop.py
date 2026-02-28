#!/usr/bin/env python3
"""
Uncrop an image. Reverses ExtractRegionFromImageByMask.
"""
import sys
from libraries.imgtools import uncrop_by_mask

def Usage(prog_name):
    print(f"""
      Copy the input image, expanding its FOV to the given full mask size. Undoes ExtractRegionFromImageByMask.

      Usage: {prog_name} input_image output_image full_mask [padding] [canvas] [log_file]
      where:
        input_image = Path to the image to be copied, using the given full mask.
        output_image = Path for the image copy to be output.
        full_mask = Path to the image whose information is used for the copy.
        padding = Optional padding value. (NOTE: this value is NOT used when also using a log_file) [default=0].
        canvas = Optional path to an image to paste the input into. [default=None]
        log_file = Optional path to a log file, previously created by the cropping (via ExtractRegionFromImageByMask). [default=None]
    """)


def main(argv=None):
    if (argv is None):
        argv = sys.argv

    # parse required arguments:
    if (len(argv) < 4):
        Usage(argv[0])
        sys.exit(1)

    input_image = argv[1]
    output_image = argv[2]
    full_mask = argv[3]

    # optional arguments with defaults:
    padding = argv[4] if (len(argv) > 4) else 0
    canvas = argv[5] if (len(argv) > 5) else None
    log_file = argv[6] if (len(argv) > 6) else None

    # do the actual work:
    uncrop_by_mask(input_image, output_image, full_mask, padding, canvas, log_file)


if __name__ == '__main__':
    main()
