import sys
import subprocess
import re


OPTION_SECTION_PATTERN = r'^OPTIONS\n(^\s+.+\n+)+'
HEADLINE_PATTERN = r'(?<=^NAME\n\s{7}).+'
FLAG_HEADLINE_PATTERN = r'^\s+%s.+.+'


def _count_spaces(s):
    for i, char in enumerate(s):
        if char != ' ':
            return i
    return 0


def main():
    command = sys.argv[1]
    flags = sys.argv[2:]

    manpage = subprocess.check_output(['man', command]).decode('utf-8')
    option_section = re.search(OPTION_SECTION_PATTERN,
                               manpage, re.MULTILINE).group(0)

    headline = re.search(HEADLINE_PATTERN, manpage, re.MULTILINE).group(0)
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
            description.append(' '*8 + line.strip())

        flag_reprs.append(flag_headline.strip() + '\n' + '\n'.join(description))

    print(headline)
    print('-' * len(headline))
    for flag_repr in flag_reprs:
        print(flag_repr, end='\n\n')


if __name__ == '__main__':
    main()
