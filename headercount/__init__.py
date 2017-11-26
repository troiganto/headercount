
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


def unquote(name):
    """Remove #include-like quotes from a string.

    This removes a single level of surrounding double quotes (`"..."`)
    or angle brackets (`<...>`) from `name`.

    Returns:

    Raises:
        ValueError: if `name` has no surrounding quotes.
    """
    if name[0] == '"' == name[-1]:
        return name[1:-1]
    elif name[0] == '<' and name[-1] == '>':
        return name[1:-1]
    else:
        raise ValueError('cannot find quotes: '+repr(name))


def iter_includes(file_):
    """Iterate over include directives in a file.

    Args:
        file_: Either a file object or a path to a file to be opened.
        ignore_system: If `True`, "#include <...>" lines are ignored.

    Returns:
        An iterator over files included by `file_`. Inclusion is
        determined by searching for #include directives.
    """
    if isinstance(file_, str):
        file_ = open(file_)
    elif isinstance(file_, Path):
        file_ = file_.open()
    for line in file_:
        line = line.lstrip()
        if not line.startswith('#'):
            continue
        parts = line[1:].split()
        if parts[0] != 'include':
            continue
        include = unquote(parts[1])
        yield include


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
    counters = [Counter(iter_includes(infile)) for infile in infiles]
    counter = sum(counters, Counter())
    for (filename, count) in sum(counters, Counter()).most_common():
        print(count, filename)
