import find_deps
import generate_website
import os
import itertools
import subprocess


def get_latest_cpython():
    pass


def remove_most_leading_zeros(string: str) -> str:
    """if the number is just 0 or 0rc1 or smth, it will keep that 0"""
    for i in range(len(string)):
        if string[i] == '0':
            continue
        if string[i] in '123456789':
            return string[i:]
        return '0' + string[i:]
    return '0'


def get_all_cpython_tags() -> list[list[str]]:
    cpython_tags = subprocess.check_output(['git', 'tag'], cwd='cpython')
    versions = [ver[1:] for ver in cpython_tags.decode().strip().split('\n') if ver[0] == 'v' and ver.count('.') == 2]
    sorted_versions = list(sorted([[s.rjust(200, '0') for s in ver.split('.')] for ver in versions]))
    rebuilt_sorted_versions = ['.'.join([remove_most_leading_zeros(s) for s in ver]) for ver in sorted_versions]
    return [[*k[1]] for k in itertools.groupby(rebuilt_sorted_versions, lambda ver: ver.split('.')[1])]


def switch_to_tag(tag: str) -> None:
    resp = subprocess.check_output(['git', 'checkout', f'tags/v{tag}'], cwd='cpython')


def main():
    if os.name != "posix":
        print('you need to do this on linux or whatever')
        exit(1)
    if (not os.path.isdir('cpython')) or (not os.path.isdir('cpython/.git')):
        print('please run: git clone https://github.com/python/cpython')
        print('this will download the cpython source in the "cpython" directory')
        print('run this script again after that')
        exit(1)
    versions = get_all_cpython_tags()
    flattened_versions = [v for l in versions for v in l]
    print('all python versions')
    print('=' * 60)
    print('\n'.join(['* ' + ', '.join(lv) for lv in versions]))
    selected_ver = '?'
    while True:
        print('\nchoose a version\n(input nothing for latest version, don\'t recommend)\n')
        selected_ver = input('> ')
        if selected_ver == '':
            selected_ver = versions[-1][-1]
        if selected_ver not in flattened_versions:
            print(f'"{selected_ver}" is not a valid version')
            continue
        break
    switch_to_tag(selected_ver)
    # todo finish script


if __name__ == "__main__":
    main()

