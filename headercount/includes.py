
"""Functions that search files for include directives."""


def get_includes_lists(paths):
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
