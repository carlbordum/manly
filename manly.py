import sys
import subprocess
import re


HEADLINE_PATTERN = r'(?<=^NAME\n\s{7}).+'
FLAG_HEADLINE_PATTERN = r'^\s+%s.+.+'
FLAG_SECTION_PATTERN = r'^%s\n(^\s+.+\n+)+'


def _count_spaces(s):
    """Return the amount of spaces at the start of *s*."""
    for count, char in enumerate(s):
        if char != ' ':
            return count
    return 0


def _get_options_section(manpage):
    """Return the part of *manpage* with flag descriptions."""
    try:
        return re.search(FLAG_SECTION_PATTERN % 'OPTIONS',
                manpage,
                re.MULTILINE,
        ).group(0)
    except AttributeError:
        return re.search(FLAG_SECTION_PATTERN % 'DESCRIPTION',
                manpage,
                re.MULTILINE,
        ).group(0)


def _format_flag_repr(headline, description):
    description[0] = description[0].capitalize()
    if description[-1][-1] != '.':
        description[-1] += '.'
    indented = [' '*8 + line for line in description]
    return '%s\n%s' % (
            headline.strip(),
            '\n'.join(indented),
    )


def _get_flag_reprs(flags, option_section):
    flag_reprs = []
    for flag in flags:
        description = []
        match = re.search(FLAG_HEADLINE_PATTERN % flag,
                          option_section, re.MULTILINE)
        flag_headline = match.group(0)[1:]
        indentation = _count_spaces(flag_headline)
        for line in option_section[match.end(0):].splitlines():
            if line == '':
                continue
            if _count_spaces(line) == indentation:
                break
            description.append(line.strip())

        flag_reprs.append(_format_flag_repr(flag_headline, description))
    return flag_reprs


def main():
    command = sys.argv[1]
    flags = sys.argv[2:]

    manpage = subprocess.check_output(['man', command]).decode('utf-8')
    headline = re.search(HEADLINE_PATTERN, manpage, re.MULTILINE).group(0)
    option_section = _get_options_section(manpage)
    flag_reprs = _get_flag_reprs(flags, option_section)

    print(headline)
    print('-' * len(headline))
    for flag_repr in flag_reprs:
        print(flag_repr, end='\n\n')


if __name__ == '__main__':
    main()
