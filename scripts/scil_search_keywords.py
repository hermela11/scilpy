#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search through all of SCILPY scripts and their docstrings. The output of the
search will be the intersection of all provided keywords, found either in the
script name or in its docstring.
"""

import argparse
import ast
import os
import pathlib
import re

import numpy as np

RED = '\033[31m'
BOLD = '\033[1m'
END_COLOR = '\033[0m'
SPACING = '=================='


def _build_arg_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('keywords', nargs='+',
                   help='Search the provided list of keywords.')

    p.add_argument('--search_parser', action='store_true',
                   help='Search through and display the full script argparser '
                        'instead of looking only at the docstring. (warning: '
                        'much slower).')
    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    # Use directory of this script, should work with most installation setups
    script_dir = pathlib.Path(__file__).parent
    matches = []

    kw_subs = [re.compile('(' + re.escape(kw) + ')', re.IGNORECASE)
               for kw in args.keywords]

    for script in sorted(script_dir.glob('*.py')):
        filename = script.name

        if args.search_parser:
            # Run the script's argparser
            help_print = os.popen('{} --help'.format(script.absolute()))
            search_text = help_print.read()
        else:
            # Fetch the docstring
            search_text = _get_docstring(str(script))

        # Test intersection of all keywords, either in filename or docstring
        if not _test_matching_keywords(args.keywords, [filename, search_text]):
            continue

        matches.append(filename)
        search_text = search_text or 'No docstring available!'

        new_key = '{}\\1{}'.format(RED + BOLD, END_COLOR)

        for regex in kw_subs:
            filename = regex.sub(new_key, filename)
            search_text = regex.sub(new_key, search_text)

        print(SPACING, filename, SPACING)
        print(search_text)
        print(SPACING, "End of {}".format(filename), SPACING)

    if not matches:
        print('No results found!')


def _test_matching_keywords(keywords, texts):
    """Test multiple texts for matching keywords. Returns True only if all
    keywords are present in any of the texts.

    Parameters
    ----------
    keywords : Iterable of str
        Keywords to test for.
    texts : Iterable of str
        Strings that should contain the keywords.

    Returns
    -------
    True if all keywords were found in at least one of the texts.

    """
    matches = []
    for key in keywords:
        key_match = False
        for text in texts:
            if key.lower() in text.lower():
                key_match = True
                break
        matches.append(key_match)

    return np.all(matches)


def _get_docstring(script):
    """Extract a python file's docstring from a filepath.

    Parameters
    ----------
    script : str
        Path to python file

    Returns
    -------
    docstring : str
        The file docstring, or an empty string if there was no docstring.
    """
    with open(script, 'r') as reader:
        file_contents = reader.read()
    module = ast.parse(file_contents)
    docstring = ast.get_docstring(module) or ''
    return docstring


if __name__ == '__main__':
    main()
