import os
import shutil  # probably should have been using this but whatever
import json


def main():
    if not os.path.isdir(os.path.join('exports', 'json')):
        print('there are no exports in ./exports/json')
        exit(1)
    else:
        json_exports = [f for f in os.listdir(os.path.join('exports', 'json')) if f.endswith('.json')]
    json_exports = list(sorted(json_exports, reverse=True))
    print('export files')
    print('=' * 60)
    print('\n'.join('* ' + fname for fname in json_exports[:15]))
    if len(json_exports) > 15:
        print(f'... ({len(json_exports)-15} hidden) ...')
    print()
    print('choose an export file')
    print('(input nothing for latest export file)')
    print()
    inp = ''
    while True:
        if inp != '':
            print(f'"{inp}" is not a valid export file')
        inp = input('> ')
        if inp in json_exports:
            break
        if inp == '':
            inp = json_exports[0]
            break
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
    print(f'you may want to run "python3 -m http.server 8080 -d exports/web" to be able to access it easily')


if __name__ == '__main__':
    main()

