
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


def prune_includes_lists(includes_lists, *, headers=False, system=False,
                         duplicates=False):
    """Remove information from the list of includes lists.

    Args:
        includes_lists: A `dict` from file `Path` to lists of
            `Include`s in that file. This `dict` is modified in-place.
        headers: Remove all header files (and their includes lists)
            from `includes_lists`.
        system: Remove all system-header includes from each list in
            `includes_lists`.
        duplicates: For each list in `includes_lists`, remove all
            duplicate `Include`s.
    """
    if headers:
        files = list(includes_lists.keys())
        for file_ in files:
            if file_.suffix in HEADER_SUFFIXES:
                del includes_lists[file_]
    if system or duplicates:
        for includes in includes_lists.values():
            filtered = includes
            if duplicates:
                filtered = set(filtered)
            if system:
                filtered = (include for include in filtered
                            if not include.is_system())
            includes[:] = filtered


def get_parser():
    """Return an argparse.ArgumentParser instance."""
    description, _, epilog = __doc__.partition("\n")
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    inctrl = parser.add_argument_group('input control')
    inctrl.add_argument('-r', '--recursive', action='store_true')
    inctrl.add_argument('--exclude', type=str, action='append', default=[])
    inctrl.add_argument('--exclude-dir', type=str, action='append', default=[])
    inctrl.add_argument('infiles', type=str, nargs='+')
    parser.add_argument('-S', '--no-system', action='store_true')
    parser.add_argument('-H', '--no-headers', action='store_true')
    parser.add_argument('-d', '--direct-only', action='store_true')
    parser.add_argument('--allow-duplicates', action='store_true')
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
    includes_lists = get_includes_lists(
        infiles,
        inclusive=not args.direct_only,
        )
    prune_includes_lists(
        includes_lists,
        system=args.no_system,
        headers=args.no_headers,
        duplicates=not args.allow_duplicates,
        )
    # Turn the lists into counters. Note: If we removed duplicates in
    # the step above, all counters will be `1` at max.
    counters = (Counter(includes) for includes in includes_lists.values())
    # Put the counters together. This is where we get the actual
    # statistics!
    total_count = sum(counters, Counter())
    # Print to stdout.
    for (filename, count) in total_count.most_common():
        print(count, filename)
