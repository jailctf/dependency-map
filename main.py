import re
import os
import time
import ast
import itertools
import json
import subprocess


DEEP_CHECK = False  # finds all methods and their dependencies too ? maybe idk, but this will compile python


# dumb regex that !mostly! fits https://docs.python.org/3/reference/grammar.html (see import_stmt)
# warning that these are NOT r strings, these are f strings
# some of these might be wrong if the import is a fake import that is in a multiline comment or smth
name = f'(?:[A-Za-z_][A-Za-z_0-9]*)'
dotted_name = f'{name}(?:\\.{name})*'
dotted_as_name = f'{dotted_name}(?:\\s+as\\s+{name})?'
dotted_as_name = f'{dotted_as_name}(?:\\s*,\\s*{dotted_as_name})*'
import_from_as_name = f'{name}(?:\\s+as\\s+{name})?'
import_from_as_names = f'{import_from_as_name}(?:\\s*,\\s*{import_from_as_name})*'
import_from_targets = f'(?:\\*|{import_from_as_names}|\\(\\s*{import_from_as_names}\\s*\\))'
import_from = f'from\\s+(?:\\.+|\\.*\\s*{dotted_name})\\s+import\\s+{import_from_targets}'
import_name = f'import\\s+{dotted_as_name}'
import_finder_regex = f'(?:{import_from}|{import_name})'

# this is an r string however !!!
delete_comments_regex = r'""".*?"""'


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
        print('\nchoose a version\n(input nothing for latest version)\n')
        selected_ver = input('> ')
        if selected_ver == '':
            selected_ver = versions[-1][-1]
        if selected_ver not in flattened_versions:
            print(f'"{selected_ver}" is not a valid version')
            continue
        break
    switch_to_tag(selected_ver)
    if DEEP_CHECK:
        print('time to build cpython')
        print('this is not finished. todo do this')
        exit(1)
    lib_filenames = os.listdir('cpython/Lib')
    py_files = [f[:-3] for f in sorted(lib_filenames) if f.endswith('.py')]  # no .py extension on strings btw
    print('found python modules:', ', '.join(py_files))
    results = {'deps': {}, 'python-version': selected_ver, 'export-timestamp': round(time.time())}
    for py_modname in py_files:
        fpath = os.path.join('cpython/Lib/', py_modname + '.py')
        print(f'searching {fpath}')
        with open(fpath, 'r') as f:
            file_lines = re.sub(delete_comments_regex, '', f.read(), re.S | re.MULTILINE).splitlines(keepends=False)
        all_finds = []  # [(line_num, is_toplvl, import_text), ...]
        for index, line in enumerate(file_lines):
            toplvl_finds = re.findall(r'^' + import_finder_regex, line)
            all_finds.extend([(index, True, imp) for imp in toplvl_finds])
            inner_finds = re.findall(r'^\s+' + import_finder_regex, line)
            all_finds.extend([(index, False, imp.lstrip()) for imp in inner_finds])
        results['deps'][py_modname] = []
        for line_num, is_toplvl, import_text in all_finds:
            tree = ast.parse(import_text)
            is_import_from = isinstance(tree.body[0], ast.ImportFrom)
            more_details = {}
            if is_import_from:
                more_details['module_name'] = tree.body[0].module
                more_details['names'] = [(alias_node.name, alias_node.name if alias_node.asname is None else alias_node.asname) 
                                         for alias_node in tree.body[0].names]
            else:
                more_details['modpaths'] = [(alias_node.name, alias_node.name if alias_node.asname is None else alias_node.asname) 
                                            for alias_node in tree.body[0].names]
            results['deps'][py_modname].append({
                'toplvl': is_toplvl,
                'import_text': import_text,
                'line_num': line_num,
                'is_import_from': is_import_from,
                **more_details
            })
    if not os.path.isdir('exports'):
        os.mkdir('exports')
    if not os.path.isdir(os.path.join('exports', 'json')):
        os.mkdir(os.path.join('exports', 'json'))
    exp_fname = os.path.join('exports', 'json', f'{selected_ver}.json')
    with open(exp_fname, 'w') as f:
        f.write(json.dumps(results, indent=4))
    print()
    print(f'successfully exported as {exp_fname}')
    print(f'you may want to run generate_website.py to generate a visualized version of this')


if __name__ == "__main__":
    main()

