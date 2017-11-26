
"""Functions that search files for include directives."""


import itertools


class AmbiguousName(Exception):
    """There is more than one matching file for an include directive."""


def get_includes_lists(paths, inclusive):
    """For each path in `paths`, return a list of included files.

    Args:
        paths: An iterable of `pathlib.Path`s to search.
        inclusive: If `True`, this lists not only a file's direct
            includes, but also its includes' includes, etc. Only files
            that are passed via `paths` are search recursively. If
            `False`, only direct includes are listed.

    Returns:
        A mapping from a file's path to the files included by said
        file (either directly or indirectly).
    """
    flat_lists = get_flat_includes_lists(paths)
    return _get_deep_includes_lists(flat_lists) if inclusive else flat_lists


def get_flat_includes_lists(paths):
    """For each path in `paths`, return a list of included files.

    Returns:
        A mapping from a file's path to the files directly included by
        said file.
    """
    includes = {}
    for path in paths:
        with path.open('r') as file_:
            includes[path] = list(iter_includes(file_))
    return includes


def _get_deep_includes_lists(flat_lists):

    """Takes the result of `get_includes_lists` and expands it."""

    include_map = _build_include_map(
        includes=set(itertools.chain.from_iterable(flat_lists.values())),
        available_files=flat_lists.keys(),
        )

    # The dict in which we collect our results.
    inclusive_lists = {}

    def _iter_project_includes(path):
        """Iterate a file's direct includes, skip those not to be searched."""
        return (include for include in flat_lists[path] if include in flat_lists)

    def _collect_all_includes(path):
        """Put together the direct and indirect includes of a file."""
        direct_includes = flat_lists[path]
        indirect_includes = (inclusive_lists.get(direct_include, [])
                             for direct_include in direct_includes)
        return list(itertools.chain(direct_includes, *indirect_includes))

    # Iterative depth-first search with a stack of iterators.
    stack = [(path, _iter_project_includes(path)) for path in flat_lists]
    while stack:
        path, includes_to_handle = stack[-1]
        include = next(includes_to_handle, None)
        if include is None:
            # We have collected all direct+indirect includes for every
            # direct include of `path`. Now we can put them together.
            inclusive_lists[path] = _collect_all_includes(path)
            stack.pop()
            continue
        # Guess which file this include directive references.
        include_file = include_map.get(include)
        if include_file and include_file not in inclusive_lists:
            # The included file is to be searched and we have not
            # searched it already. Thus, we descend into it.
            stack.append((include_file, _iter_project_includes(include_file)))

    return inclusive_lists


def _build_include_map(includes, available_files):
    """Build a map of guesses which include directive maps to which file.

    Args:
        includes: A list of `Include` objects.
        available_files: A list of files that the include directives
            could possibly map to.

    Returns:
        A mapping `include => available_file` of all `include`s for
        which a file could be found.

    Raises:
        `AmbiguousName` if there are several candidates for a given
        `include`.
    """
    result = {}
    for include in includes:
        candidates = [path for path in available_files
                      if path.name == include.unquoted()]
        if len(candidates) > 1:
            raise AmbiguousName(str(include))
        elif candidates:
            (result[include],) = candidates
    return result


def iter_includes(file_):
    """Iterate over include directives in a file.

    Args:
        file_: A file object to read from.
        ignore_system: If `True`, "#include <...>" lines are ignored.

    Returns:
        An iterator over files included by `file_`. Inclusion is
        determined by searching for #include directives.
    """
    for line in file_:
        line = line.lstrip()
        if not line.startswith('#'):
            continue
        parts = line[1:].split()
        if parts[0] != 'include':
            continue
        yield Include(parts[1])


class Include:

    __slots__ = ['_inner']

    def __init__(self, include):
        is_system = include[0] == '<' and include[-1] == '>'
        is_regular = include[0] == '"' == include[-1]
        if not (is_system or is_regular):
            raise ValueError('cannot find quotes: '+repr(include))
        self._inner = include

    def __str__(self):
        return self._inner

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, repr(self._inner))

    def is_system(self):
        return self._inner[0] == '<'

    def unquoted(self):
        return self._inner[1:-1]
