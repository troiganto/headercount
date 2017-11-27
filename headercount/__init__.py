
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

from headercount.files import HEADER_SUFFIXES
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
    parser.add_argument('--mode', default='inclusive-unique',
                        choices=['direct', 'inclusive', 'inclusive-unique'])
    parser.add_argument('-S', '--no-system', action='store_true')
    parser.add_argument('-H', '--no-headers', action='store_true')
    return parser


def main(argv):
    """Main function. You should pass `sys.argv[1:]` as argument."""
    args = get_parser().parse_args(argv)
    # Build the list of files that are to be searched.
    infiles = iter_input_files(
        args.infiles,
        recursive=args.recursive,
        exclude=args.exclude,
        exclude_dir=args.exclude_dir
        )
    # Search each file for a list of included files -- either
    # direct+indirect includes or direct includes only.
    includes_lists = get_includes_lists(infiles, 'inclusive' in args.mode)
    # Filter out all system header includes.
    if args.no_system:
        for includes in includes_lists.values():
            filtered = [include for include in includes
                        if not include.is_system()]
            includes[:] = filtered
    # Filter out all header files so we don't count their includes twice.
    if args.no_headers:
        includes_lists = {path: includes
                          for (path, includes) in includes_lists.items()
                          if path.suffix not in HEADER_SUFFIXES}
    # Turn the lists into sets if we are not interested in duplicates.
    # (Otherwise, a single file might seem to `#include <vector>`
    # dozens of times.)
    if 'unique' in args.mode:
        includes_lists = {
            path: set(includes)
            for (path, includes) in includes_lists.items()
            }
    # Turn the lists into counters. Note: If we removed duplicates in
    # the step above, all counters will be `1` at max.
    counters = (Counter(includes) for includes in includes_lists.values())
    # Put the counters together. This is where we get the actual
    # statistics!
    total_count = sum(counters, Counter())
    # Print to stdout.
    for (filename, count) in total_count.most_common():
        print(count, filename)
