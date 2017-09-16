import sys
import subprocess
import re


HEADLINE_PATTERN = r'(?<=^NAME\n\s{7}).+'
FLAG_HEADLINE_PATTERN = r'^\s+%s.+.+'
FLAG_SECTION_PATTERN = r'^%s\n(^\s+.+\n+)+'


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


def get_flags(manpage):
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


def format_flag_repr(headline, description):
    description[0] = description[0].capitalize()
    if description[-1][-1] != '.':
        description[-1] += '.'
    indented = [' '*8 + line for line in description]
    return '%s\n%s' % (
            headline.strip(),
            '\n'.join(indented),
    )


def get_flag_reprs(flags, option_section):
    flag_reprs = []
    for flag in flags:
        description = []
        match = re.search(FLAG_HEADLINE_PATTERN % flag,
                          option_section, re.MULTILINE)
        flag_headline = match.group(0)[1:]
        indentation = count_spaces(flag_headline)
        for line in option_section[match.end(0):].splitlines():
            if line == '':
                continue
            if count_spaces(line) == indentation:
                break
            description.append(line.strip())

        flag_reprs.append(format_flag_repr(flag_headline, description))
    return flag_reprs


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


def main():
    command = sys.argv[1]
    flags = parse_flags(sys.argv[2:])

    manpage = subprocess.check_output(['man', command]).decode('utf-8')
    headline = re.search(HEADLINE_PATTERN, manpage, re.MULTILINE).group(0)
    option_section = get_options_section(manpage)
    flag_reprs = get_flag_reprs(flags, option_section)

    print(headline)
    print('-' * len(headline))
    for flag_repr in flag_reprs:
        print(flag_repr, end='\n\n')


if __name__ == '__main__':
    main()
