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
__version__ = "0.4.1"


import argparse
import functools
import os
import re
import sys
import string
import subprocess
from subprocess import CalledProcessError


print_err = functools.partial(print, file=sys.stderr)


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


def remove_non_printable(text: str) -> str:
    printable_set = set(string.printable)
    return ''.join(char for char in text if char in printable_set)


def make_bold(text: str) -> str:
    if sys.stdout.isatty():
        return f"\033[1m{text}\033[0m"
    return text


def highlight_flags_in_section(flag: str, section: str) -> str:
    return re.sub(rf"(^|\s){flag}", make_bold(flag), section).rstrip()


def extract_title_from_manpage(manpage: str) -> str:
    match = re.search(r"^NAME\s*\n\s*(.+?)\s*$", manpage, re.MULTILINE)
    if match:
        return make_bold(match.group(1).strip())
    return "Title not found"


def print_output(title: str, output: list) -> None:
    if output:
        print(f"\n{title}")
        print("=" * (len(title) - 8), end="\n\n")

        for flag in output:
            print(f"{flag}\n")
    else:
        print(f"{make_bold('manly')}: No matching flags found.")


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
        # Split and separately add potential single-letter flags
        if not flag.startswith("--"):
            flags.update("-" + char for char in flag[1:])
    return list(flags)


def parse_manpage(page, flags):
    """Return a list of blocks that match *flags* in *page*."""
    current_section = []
    output = []
    inside_flag_section = None

    for line in page.splitlines():
        stripped_line = line.strip()

        if stripped_line:
            # Check for any flag in this line
            for flag in flags:
                if stripped_line.startswith(flag):
                    # Finish the previous section, if any
                    if inside_flag_section is not None:
                        output.append("\n".join(current_section).rstrip())
                        current_section = []

                    # Start a new section
                    inside_flag_section = flag
                    current_section.append(
                        highlight_flags_in_section(flag, stripped_line)
                    )
                    break
            else:
                if inside_flag_section is not None:
                    # Add spaces to the left of inside sections
                    indented_line = "       " + stripped_line
                    current_section.append(indented_line)
        else:
            if inside_flag_section is not None:
                output.append("\n".join(current_section).rstrip())
                current_section = []
                inside_flag_section = None

    return output


def manly(command):
    if isinstance(command, str):
        command = command.split(" ")
    program = command[0]
    flags = command[1:]
    # we set MANWIDTH, so we don't rely on the users terminal width
    # try `export MANWIDTH=80` -- makes manuals more readable imo :)
    man_env = {}
    man_env.update(os.environ)
    man_env["MANWIDTH"] = "80"
    try:
        command = f"man {program} | col -b"

        process = subprocess.Popen(
            command,
            env=man_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        out, err = (s.decode("utf-8") for s in process.communicate())

        # Check for errors
        if process.returncode:
            raise CalledProcessError(process.returncode, command, out, err)
    except OSError as e:
        print_err("manly: Could not execute 'man'")
        print_err(e)
        sys.exit(127)
    except CalledProcessError as e:
        print_err(e.stderr.strip())
        sys.exit(e.returncode)

    sanitized_manpage = remove_non_printable(out)
    title = extract_title_from_manpage(sanitized_manpage)
    flags = parse_flags(flags)
    output = parse_manpage(sanitized_manpage, flags)
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
        print_err(
            "manly: missing COMMAND\nTry 'manly --help' for more information.",
        )
        sys.exit(1)

    title, output = manly(args.command)
    print_output(title, output)

if __name__ == "__main__":
    main()
