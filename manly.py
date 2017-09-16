import sys
import subprocess
import re


def count_spaces(s):
    """Return the amount of spaces at the start of *s*."""
    for count, char in enumerate(s):
        if char != ' ':
            return count
    return 0


def get_headlines(manpage_lines):
    """Return a list with (headline, index) for all flags."""
    headlines = []
    for i, headline in enumerate(manpage_lines):
        if re.match(r'\s+--?\w', headline):
            headlines.append((headline, i))
    return headlines


def parse_manpage(manpage):
    """Return (headline, description) for all flags in *manpage*."""
    lines = manpage.splitlines()
    flags = []
    for headline, index in get_headlines(lines):
        description = []
        indentation = count_spaces(headline)
        i = index+1
        next_line = lines[i]
        next_indentation = count_spaces(next_line)
        if next_indentation == 0:
            i += 1
            next_line = lines[i]
            next_indentation = count_spaces(next_line)
        if next_indentation <= indentation:
            continue
        while count_spaces(next_line) == next_indentation:
            description.append(next_line.strip())
            i += 1
            next_line = lines[i]
        flags.append((headline.strip(), description))
    return flags


def parse_flags(raw_flags):
    """Return a list of the flags in *raw_flags*."""
    flags = []
    for raw_flag in raw_flags:
        if raw_flag.startswith('--'):
            flags.append(raw_flag[:raw_flag.find('=')])
        elif raw_flag.startswith('-'):
            for flag in raw_flag[1:]:
                flags.append('-' + flag)
    return flags


def format_headline(headline):
    return headline


def format_description(description):
    return description


def main():
    command = sys.argv[1]
    flags = parse_flags(sys.argv[2:])

    manpage = subprocess.check_output(['man', command]).decode('utf-8')
    parsed_manpage = parse_manpage(manpage)

    for flag in flags:
        for headline, description in parsed_manpage:
            if flag in headline:
                print(format_headline(headline))
                print(format_description(description))


if __name__ == '__main__':
    main()
