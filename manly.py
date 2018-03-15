"""
    manly
    ~~~~~
    This script is used (through its' cli) to extract information from
    manual pages. More specifically, it tells the user, how the given
    flags modify a programs behaviour.
"""


__author__ = 'Carl Bordum Hansen'
__version__ = '0.3.0'


import sys
import subprocess
import re


_ANSI_BOLD = '\033[1m{}\033[0m'


HELP = """Usage: manly COMMAND FLAGS...
explain commands

Example:
    $ manly rm -r

    rm - remove files or directories
    ================================

        -r, -R, --recursive
                remove directories and their contents recursively


Arguments:
  -h, --help            display this help and exit.
  -v, --version         display version information and exit.

Project resides at <https://github.com/Zaab1t/manly>"""
VERSION = ('manly %s\nCopyright (c) 2017 %s.\nMIT License: see LICENSE.\n\n'
           'Written by %s and Mark Jameson.') % (
                   __version__, __author__, __author__)


def parse_flags(raw_flags, single_dash=False):
    '''Split concatenated flags (eg. ls' -la) into individual flags
    (eg. '-la' -> '-l', '-a').

    Args:
        raw_flags (list): The flags as they would be given normally.
        single_dash (bool): Indicate whether a manpage use long names
            prefixed with only one dash e.g. -nostdinc

    Returns:
        flags (list): The disassembled concatenations of flags, and regular
            verbose flags as given.
    '''
    flags = []
    for flag in raw_flags:
        if flag.startswith('--') or single_dash:
            flags.append(flag)
        elif flag.startswith('-'):
            for char in flag[1:]:
                flags.append('-' + char)
    return flags


def parse_manpage(page, args):
    '''Scan the manpage for blocks of text, and check if the found blocks
    have sections that match the general manpage-flag descriptor style.

    Args:
        page (str): The utf-8 encoded manpage.
        args (iter): An iterable of flags passed to check against.

    Returns:
        output (list): The blocks of the manpage that match the given flags.
    '''
    current_section = []
    output = []

    for line in page.splitlines():
        line = line + '\n'
        if line != '\n':
            current_section.append(line)
            continue

        section = ''.join(current_section)
        section_top = section.strip().split('\n')[:2]
        first_line = section_top[0].split(',')

        for arg in args:
            try:
                if any(seg.strip().startswith(arg) for seg in first_line) \
                  or section_top[1].strip().startswith(arg):
                    section = re.sub(r'(^|\s){}'.format(arg),
                                     _ANSI_BOLD.format(arg),
                                     section)
                    output.append(section.rstrip())
                    break
            except IndexError:
                pass
        current_section = []
    return output


def main():
    # HANDLE ALL INPUT
    try:
        command = sys.argv[1]
    except IndexError:
        print("manly: missing COMMAND\n"
              "Try 'manly --help' for more information.")
        sys.exit(0)
    if len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help'):
            print(HELP)
            sys.exit(0)
        if sys.argv[1] in ('-v', '--version'):
            print(VERSION)
            sys.exit(0)
        print("manly: missing flags\n"
              "Try 'manly --help' for more information.")
        sys.exit(2)
    if sys.argv[1] == 'manly':
        print('There are no turtles.')
        sys.exit(0)
    try:
        manpage = subprocess.check_output(
            ['(export MANWIDTH=80; man %s)' % command],
            shell=True,
        ).decode('utf-8')
    except subprocess.CalledProcessError:
        sys.exit(16)  # because that's the exit status that `man` uses.

    # LOGIC
    uses_single_dash_names = any((re.match(r'\s+-\w{2,}', line) for line in
                                  manpage.splitlines()))
    flags = parse_flags(sys.argv[2:], uses_single_dash_names)
    output = parse_manpage(manpage, flags)
    title = _ANSI_BOLD.format(
            re.search(
                r'(?<=^NAME\n\s{5}).+',
                manpage,
                re.MULTILINE
            ).group(0).strip())

    # OUTPUT
    if output:
        print('\n%s' % title)
        print('=' * (len(title) - 8), end='\n\n')
        for flag in output:
            print(flag, end='\n\n')
    else:
        print('No flags found.')


if __name__ == '__main__':
    main()
