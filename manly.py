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
__version__ = "0.4.0"


import argparse
import re
import subprocess
import sys


# A backport from subprocess to cover differences between 2/3.4 and 3.5
# This allows the same args to be passed into CPE regardless of version.
# This can be replaced with an import at 2.7 EOL
# See: https://github.com/carlbordum/manly/issues/27
class CalledProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, output=None, stderr=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr


_ANSI_BOLD = "%s"
if sys.stdout.isatty():
    _ANSI_BOLD = "\033[1m%s\033[0m"

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


def parse_flags(raw_flags):
    """Return a list of flags.

    Concatenated flags will be split into individual flags
    (eg. '-la' -> '-l', '-a'), but the concatenated flag will also be
    returned, as some command use single dash names (e.g `clang` has
    flags like "-nostdinc") and some even mix both.
    """
    flags = set()
    for flag in raw_flags:
        # Filter out non-flags
        if not flag.startswith("-"):
            continue
        flags.add(flag)
        # Split and sperately add potential single-letter flags
        if not flag.startswith("--"):
            flags.update("-" + char for char in flag[1:])
    return list(flags)


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
    try:
        process = subprocess.Popen(
            ["man", "--", program],
            env={"MANWIDTH": "80"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = (s.decode("utf-8") for s in process.communicate())
        # emulate subprocess.run of py3.5, for easier changing in the future
        if process.returncode:
            raise CalledProcessError(
                process.returncode, ["man", "--", program], out, err
            )
    except OSError as e:
        print("manly: Could not execute 'man'", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(127)
    except CalledProcessError as e:
        print(e.stderr.strip(), file=sys.stderr)
        sys.exit(e.returncode)

    manpage = out
    flags = parse_flags(flags)
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
        print(
            "manly: missing COMMAND\nTry 'manly --help' for more information.",
            file=sys.stderr,
        )
        sys.exit(0)

    title, output = manly(args.command)
    if output:
        print("\n%s" % title)
        print("=" * (len(title) - 8), end="\n\n")
        for flag in output:
            print(flag, end="\n\n")
    else:
        print("manly: No matching flags found.", file=sys.stderr)


if __name__ == "__main__":
    main()
