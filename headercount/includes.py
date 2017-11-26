
"""Functions that search files for include directives."""


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
        return sum(indirect_includes, direct_includes)

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
        elif include not in inclusive_lists:
            # We have not found the includes of this include yet --
            # descend into it.
            stack.append((include, _iter_project_includes(include)))
        else:
            # We have handled this include already or the user has not
            # requested it to be searched.
            pass

    return inclusive_lists


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
        include = unquote(parts[1])
        yield include


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
