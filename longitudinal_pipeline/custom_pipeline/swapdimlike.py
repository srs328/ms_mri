#!/usr/bin/env python3
"""
Swaps dimension ordering (reslices) of input image to match another.
"""
import os
import sys

from libraries.imgtools import swapdimlike

def Usage(prog_name):
    print(f"""
      Copy the input image, reordering the axes of the copy to match those of the given "like" image.

      Usage: {prog_name} input_image like_image, output_image
      where:
        input_image = Path to the image to be copied, using the additional "like" image.
        like_image = Path to the image whose information is used to reorder the axes.
        output_image = Path to the output (reordered copy) image.
    """)


def main(argv=None):
    if (argv is None):
        argv = sys.argv

    # parse required arguments:
    if (len(argv) < 4):
        Usage(argv[0])
        sys.exit(1)

    input_image = sys.argv[1]
    like_image = sys.argv[2]
    output_image = sys.argv[3]

    for img in [input_image, like_image]:
        if (not os.path.exists(img)):
            print(f"Unable to find file: '{img}'")
            sys.exit(1)

    # defer to image tools function to do the work
    swapdimlike(input_image, like_image, output_image)



if __name__ == '__main__':
    main()
