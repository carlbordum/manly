import sys
import subprocess
import re


_ANSI_BOLD = '\033[1m{}\033[0m'


def parse_flags(raw_flags):
    '''Split concatenated flags (eg. ls' -la) into individual flags
    (eg. '-la' -> '-l', '-a').

    Args:
        raw_flags (list): The flags as they would be given normally.

    Returns:
        flags (list): The disassembled concatenations of flags, and regular
            verbose flags as given.
    '''
    flags = []
    for flag in raw_flags:
        if flag.startswith('-'):
            if not flag.startswith('--'):
                flag = flag.replace('-', '')
                for char in flag:
                    flags.append('-' + char)
            else:
                flags.append(flag)
        else:
            pass
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
    command = sys.argv[1]
    flags = parse_flags(sys.argv[2:])
    manpage = subprocess.check_output(['man', command]).decode('utf-8')

    title = _ANSI_BOLD.format(re.search(r'(?<=^NAME\n\s{7}).+', manpage, re.MULTILINE).group(0))
    output = parse_manpage(manpage, flags)

    print('\nSearching for:', command, *flags, '\n')
    if output:
        print(title)
        print('-' * len(title), '\n')
        for flag in output:
            print(flag, '\n')
    else:
        print('No flags found.')
    print()


if __name__ == '__main__':
    main()
