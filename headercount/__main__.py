#!/usr/bin/env python3

"""Launcher for `headercount`."""

import sys

import headercount


def main():
    """The main function."""
    sys.exit(headercount.main(sys.argv[1:]))

if __name__ == "__main__":
    main()
