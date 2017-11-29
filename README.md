Headercount – Count which header is included how many times
===========================================================

Headercount is a small debugging script that is meant to help
developers who are trying to cut down compile times in a medium-sized
C++ project.

Headercount recursively searches a project for #include and prints
statistics about which header was included how many times. This
indicates which headers are depended on the most. With this
information, a developer knows where to start with methods such as the
PIMPL idiom, forward declarations, reduction of templatization, etc.

Installation
------------

Headercount is a Python package based on [Setuptools][]. It requires
Python 3.4 or higher. It has no dependencies beyond the Python standard
library. The easiest way to install it is via pip:

```bash
pip3 install headercount
```

You can also download the latest wheel from the [Releases][] page and
install that:

```bash
pip3 install headercount-<VERSION>-py3-none-any.whl
```

Finally, you can also install Headercount manually by cloning this
repository:

```bash
git clone https://github.com/troiganto/headercount
cd headercount
python3 setup.py install
```

Working Principle
-----------------

Headercount works on a best-effort basis and may give incorrect results
when faced with strange include pattern. Contributions to improve the
algorithm are highly welcome!

For any given input file, Headercount checks whether it is a C/C++ file
based on its file name suffix. Non-matching files are ignored.
Directories are ignored as well, unless `--recursive` is passed; if it
is, directories are searched recursively for C/C++ files.

Any accepted file is searched for `#include <...>` and `#include "..."`
directives. Any found directive is counted towards the final tally.
Additionally, Headercount attempts to match each include directive to
one of its input files, based on the input files' base names. If such a
match succeeds, the includes of the matched files are added to the list
of includes found in the originally searched file.

This means that a header file is not searched for additional includes
if it is not specified on the command line. This helps make the
behavior of Headercount predictable.

Finally, the total numbers are tallied for each include across all
input files.

The following arguments allow to modify this default behavior:

- `--no-headers`: Only source files (as termined by the file name
  suffix) are used to form the final tally. Header files are only used
  to determine recursive dependencies. This is useful for many
  developers, who are only interested in the impact of an include on
  compilation times.

- `--no-system`: The final tally excludes all `#include <...>`-style
  directives. This is useful if the developer is only interested in
  intra-project dependencies.

- `--direct-only`: No recursive search is done. The tally only counts
  literal `#include` directives.

- `--allow-duplicates`: If a file is included multiple times (literally
  or due to indirect includes), all occurrences are counted.

Contributing
------------

Headercount is only a tiny project made by a tiny guy. Any help is
highly encouraged. If you wish to contribute, simply open an issue or
send a pull request.

Headercount supports Python 3.4, C11, and C++11 and onwards. If it does
not, it is a bug and should be reported. It uses [Pep8][] and uses
[PyLint][] for style checking. Before sending a pull request, please
make sure that these tools don't give any warnings.


[Releases]: https://github.com/troiganto/headercount/releases
[Pep8]: https://pypi.python.org/pypi/pep8
[PyLint]: https://pypi.python.org/pypi/pylint
[Setuptools]: https://pypi.python.org/pypi/setuptools
