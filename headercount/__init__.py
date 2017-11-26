
"""Count which header is included how many times.

This script combs through a C/C++ project and counts for each file how
many times it was included by another file. This count is usually done
inclusively, i.e. a headers included by other headers are counted
multiple times. But exclusive counts are possible, too.
"""

import sys
import argparse
from pathlib import Path
from collections import Counter

from headercount.files import iter_input_files
from headercount.includes import get_includes_lists


def get_parser():
    """Return an argparse.ArgumentParser instance."""
    description, _, epilog = __doc__.partition("\n")
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    parser.add_argument('infiles', type=str, nargs='+')
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.add_argument('--exclude', type=str, action='append', default=[])
    parser.add_argument('--exclude-dir', type=str, action='append', default=[])
    return parser


def main(argv):
    """Main function. You should pass `sys.argv[1:]` as argument."""
    args = get_parser().parse_args(argv)
    infiles = iter_input_files(
        args.infiles,
        recursive=args.recursive,
        exclude=args.exclude,
        exclude_dir=args.exclude_dir
        )
    counters = [
        Counter(includes)
        for (_, includes) in get_includes_lists(infiles).items()
        ]
    counter = sum(counters, Counter())
    for (filename, count) in sum(counters, Counter()).most_common():
        print(count, filename)
