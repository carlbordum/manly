#!/usr/bin/env python

"""
    manly
    ~~~~~
    This script is used (through its' cli) to extract information from
    manual pages. More specifically, it tells the user, how the given
    flags modify a command's behaviour.

    In the code "options" refer to options for manly and "flags" refer
    to options for the given command.
"""


from __future__ import print_function


__author__ = "Carl Bordum Hansen"
__version__ = "0.3.3"


import argparse
import re
import subprocess
import sys


_ANSI_BOLD = "\033[1m%s\033[0m"
if not sys.stdout.isatty():
    _ANSI_BOLD = "%s"

USAGE_EXAMPLE = """example:
    $ manly rm --preserve-root -rf

    rm - remove files or directories
    ================================

        -f, --force
                ignore nonexistent files and arguments, never prompt

        --preserve-root
                do not remove '/' (default)

        -r, -R, --recursive
                remove directories and their contents recursively"""

VERSION = (
    "manly %s\nCopyright (c) 2017 %s.\nMIT License: see LICENSE.\n\n"
    "Written by %s and Mark Jameson."
) % (__version__, __author__, __author__)


def parse_flags(raw_flags, single_dash=False):
    """Return a list of flags.

    If *single_dash* is False, concatenated flags will be split into
    individual flags (eg. '-la' -> '-l', '-a').
    """
    flags = []
    for flag in raw_flags:
        if flag.startswith("--") or single_dash:
            flags.append(flag)
        elif flag.startswith("-"):
            for char in flag[1:]:
                flags.append("-" + char)
    return flags


def parse_manpage(page, flags):
    """Return a list of blocks that match *flags* in *page*."""
    current_section = []
    output = []

    for line in page.splitlines():
        if line:
            current_section.append(line)
            continue

        section = "\n".join(current_section)
        section_top = section.strip().split("\n")[:2]
        first_line = section_top[0].split(",")

        segments = [seg.strip() for seg in first_line]
        try:
            segments.append(section_top[1].strip())
        except IndexError:
            pass

        for flag in flags:
            for segment in segments:
                if segment.startswith(flag):
                    output.append(
                        re.sub(r"(^|\s)%s" % flag, _ANSI_BOLD % flag, section).rstrip()
                    )
                    break
        current_section = []
    return output


def manly(command):
    if isinstance(command, str):
        command = command.split(" ")
    program = command[0]
    flags = command[1:]

    # we set MANWIDTH, so we don't rely on the users terminal width
    # try `export MANWIDTH=80` -- makes manuals more readable imo :)
    process = subprocess.Popen(
        "export MANWIDTH=80; man %s" % program,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    out, err = process.communicate()

    if process.returncode == 0:
        manpage = out.decode("utf-8")
    else:
        if process.returncode == 126:
            error_msg = "Error: 'man' is not executable."
        elif process.returncode == 127:
            error_msg = "Error: 'man' not found in your path. Please install it or add it to your path.2w"
        else:
            error_msg = err.decode("utf-8")
        print(error_msg, file=sys.stdout)
        sys.exit(process.returncode)

    # commands such as `clang` use single dash names like "-nostdinc"
    uses_single_dash_names = bool(re.search(r"\n\n\s+-\w{2,}", manpage))
    flags = parse_flags(flags, single_dash=uses_single_dash_names)
    output = parse_manpage(manpage, flags)
    title = _ANSI_BOLD % (
        re.search(r"(?<=^NAME\n\s{5}).+", manpage, re.MULTILINE).group(0).strip()
    )

    return title, output


def main():
    parser = argparse.ArgumentParser(
        prog="manly",
        description="Explain how FLAGS modify a COMMAND's behaviour.",
        epilog=USAGE_EXAMPLE,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=VERSION,
        help="display version information and exit.",
    )
    args = parser.parse_args()

    if not len(args.command):
        print("manly: missing COMMAND\n" "Try 'manly --help' for more information.")
        sys.exit(0)

    title, output = manly(args.command)
    if output:
        print("\n%s" % title)
        print("=" * (len(title) - 8), end="\n\n")
        for flag in output:
            print(flag, end="\n\n")
    else:
        print("No flags found.")


if __name__ == "__main__":
    main()
