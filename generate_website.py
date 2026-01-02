import os
import shutil  # probably should have been using this but whatever
import json
import re


def sort_version(version_s):
    split = version_s.removesuffix('.json').split('.')
    total = []
    for w in split:
        try:
            total.append(int(w))
        except:
            total.append(w)
    if isinstance(total[-1], str):
        last = total.pop(-1)
        last_better = []
        if 'a' in last:
            last_split = last.split('a')
            last_better = [int(last_split[0]), 0, int(last_split[1])]
        elif 'b' in last:
            last_split = last.split('b')
            last_better = [int(last_split[0]), 1, int(last_split[1])]
        elif 'rc' in last:
            last_split = last.split('rc')
            last_better = [int(last_split[0]), 2, int(last_split[1])]
        else:
            raise NotImplementedError("bad version for sorting: " + version_s)
        total.extend(last_better)
    else:
        while len(total) < 3:
            total.append(3)
        if len(total) == 3:
            total.extend([3, 0])
        if len(total) == 4:
            total.append(0)
    return tuple(total)


def gen_website(inp):
    print('generating website from template.html')
    with open(os.path.join('exports', 'json', inp), 'r') as f:
        data_str = json.dumps(json.load(f))
    with open('template.html', 'r') as f:
        template_used = f.read().replace('{!{DATA}!}', data_str, 1).replace('{!{VERSION}!}', inp.removesuffix('.json'), 1)
    if not os.path.isdir(os.path.join('exports', 'web')):
        os.mkdir(os.path.join('exports', 'web'))
    shutil.copyfile('cytoscape.min.js', os.path.join('exports', 'web', 'cytoscape.min.js'))
    shutil.copyfile('cytoscape-cola.js', os.path.join('exports', 'web', 'cytoscape-cola.js'))
    html_file_path = os.path.join('exports', 'web', inp.removesuffix('.json') + '.html')
    with open(html_file_path, 'w') as f:
        f.write(template_used)
    print(f'successfully exported as {html_file_path}')


def main():
    if not os.path.isdir(os.path.join('exports', 'json')):
        print('there are no exports in ./exports/json')
        exit(1)
    else:
        json_exports = [f for f in os.listdir(os.path.join('exports', 'json')) if f.endswith('.json')]
    json_exports = list(sorted(json_exports, reverse=True, key=sort_version))
    print('export files')
    print('=' * 60)
    print('\n'.join('* ' + fname for fname in json_exports[:15]))
    if len(json_exports) > 15:
        print(f'... ({len(json_exports)-15} hidden) ...')
    print()
    print('choose an export file')
    print('(input nothing for latest export file)')  # idk if latest lol
    print('(input "all" for all export files)')
    print()
    inp = ''
    while True:
        if inp != '':
            print(f'"{inp}" is not a valid export file')
        inp = input('> ')
        if inp in json_exports:
            gen_website(inp)
            break
        if inp == 'all':
            for export_file in json_exports:
                gen_website(export_file)
            break
        if inp == '':
            inp = json_exports[0]
            gen_website(inp)
            break
    print('generating index.html')
    with open('index-template.html', 'r') as f:
        index_html = f.read()
    with open(os.path.join('exports', 'web', 'index.html'), 'w') as f:
        per_version_htmls = {}
        for version in json_exports:
            version_split = sort_version(version)
            if version_split[:2] not in per_version_htmls:
                per_version_htmls[version_split[:2]] = []
            per_version_htmls[version_split[:2]].append(f'<a href="{version.removesuffix(".json")}.html" target="_blank">{version.removesuffix(".json")}</a>')
        pages_html = '<br>'.join(['<p>' + ', '.join(per_version_htmls[v]) + '</p>' for v in sorted(per_version_htmls, reverse=True)])
        index_html = index_html.replace('{!{PAGESHTML}!}', pages_html)
        f.write(index_html)
    print('successfully generated index.html')
    print(f'you may want to run "python3 -m http.server 8080 -d exports/web" to be able to access it easily')


if __name__ == '__main__':
    main()

