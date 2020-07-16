import sys
import os
import json
import ast
import glob

from ansible.parsing.plugin_docs import read_docstring
from ansible.parsing.yaml.loader import AnsibleLoader
from ansible import __version__


line_ct = 0


excludes = (
    # genuinely bad yaml, the command gives error:
    # ansible-doc google.cloud.gcp_pubsub_subscription
    'google/cloud/plugins/modules/gcp_pubsub_subscription.py',
)
req_data = {}


EXCLUDE_REQUIREMENTS = frozenset((
    'ansible',
    'ansible-base',
    'python',
    'yaml', 'pyyaml',
    'six.moves.stringio', 'sys',
    '',
    'tox', 'pycodestyle', 'yamllint', 'voluptuous', 'pylint',
    'flake8', 'pytest', 'pytest-xdist', 'coverage', 'mock',
    'requests',
    'json',
    'ansible-lint', 'molecule', 'ssl',
    'whitelist in configuration'
))


def pkg(req):
    p = None
    for sep in frozenset(('==', '>=', '>', '<', '<=')):
        if sep in req:
            new_p = req.split(sep, 1)[0].strip()
            # If one of these occurs earlier than others, use that
            if p is None or len(new_p) < len(p):
                p = new_p
    if p is not None:
        return p.lower().strip('.').strip()
    return req.lower().strip('.').strip()


def exclude_req(req):
    if req.startswith('-r ') or req.startswith('#'):
        return True
    if pkg(req) in EXCLUDE_REQUIREMENTS:
        return True
    return False


def add_req(alist, req):
    if exclude_req(req) or req in alist:
        return
    for i in range(len(alist)):
        existing_req = alist[i]
        existing_pkg = pkg(existing_req)
        new_pkg = pkg(req)
        if new_pkg == existing_pkg:
            new_spec = req[len(new_pkg):].strip()
            if not new_spec or new_spec in existing_req:
                return
            if existing_pkg == existing_req:
                alist[i] = ' '.join([existing_req, new_spec])
            else:
                alist[i] = ','.join([existing_req, new_spec])
            return
    alist.append(req)


def ast_fragment_parse(path):
    with open(path, 'rb') as f:
        M = ast.parse(f.read())
    # only one class per doc fragment
    file_classes = [thing for thing in M.body if isinstance(thing, ast.ClassDef)]
    assert len(file_classes) == 1, (M.body, path)
    cls = file_classes[0]
    assert isinstance(cls, ast.ClassDef)
    # doc fragments are allowed to have >1 definition per doc fragment file, see:
    # target/ansible_collections/netapp/ontap/plugins/doc_fragments/netapp.py
    # referenced as netapp.ontap.netapp.na_ontap
    fragments = {}
    for thedef in cls.body:
        assert isinstance(thedef, ast.Assign), thedef
        assert len(thedef.targets) == 1
        key = thedef.targets[0].id
        assert isinstance(thedef.value, ast.Str)
        data = AnsibleLoader(thedef.value.s, file_name=path).get_single_data()
        fragments[key] = data
    return fragments


# TODO: figure out how to make this not crazy hacky
target_pythonpath = os.path.join('target', 'ansible_collections')
for namespace in os.listdir(target_pythonpath):
    namespace_dir = os.path.join(target_pythonpath, namespace)
    for name in os.listdir(namespace_dir):
        if namespace == 'ansible' and name == 'base' and __version__.startswith('2.9'):
            print('skipping ansible.base b/c not a thing in 2.9')
            continue
        fqcn = f'{namespace}.{name}'
        req_data.setdefault(fqcn, [])
        collection_dir = os.path.join(namespace_dir, name)
        top_content = os.listdir(collection_dir)

        collection_dir = os.path.join(target_pythonpath, namespace, name)
        for candidate in os.listdir(collection_dir):
            # no thanks to python2
            if ('requirement' in candidate) and ('txt' in candidate) and ('2.7' not in candidate):
                with open(os.path.join(collection_dir, candidate), 'r') as f:
                    req_text = f.read()
                req_text = req_text.strip()
                for line in req_text.split('\n'):
                    add_req(req_data[fqcn], line)


for path in glob.iglob(target_pythonpath.strip(os.path.sep) + '/**/*.py', recursive=True):

    path_parts = path.split(os.path.sep)
    assert path_parts[1] == 'ansible_collections', path_parts
    namespace = path_parts[2]
    name = path_parts[3]
    if len(path_parts) < 7:
        continue  # no plugins and type folder like plugins/modules, plugins/inventory
    if path_parts[4] != 'plugins':
        continue
    if path_parts[5] in ('terminal',):
        continue
    fname = path_parts[-1]
    if fname in ('__init__.py',):
        continue

    collection = '{}.{}'.format(namespace, name)
    req_data.setdefault(collection, [])

    if any(path.endswith(exclude) for exclude in excludes):
        continue
    assert os.path.exists(path)

    if path_parts[5] == 'doc_fragments':
        fragments = ast_fragment_parse(path)
        check_requirements = list(fragments.values())
    else:
        plugin_data = read_docstring(path, verbose=False)['doc']
        check_requirements = [plugin_data]

    for plugin_data in check_requirements:
        if plugin_data is None:
            # print(f'Suspicious of plugin: {path}')
            assert len(check_requirements) == 1
            with open(path, 'r') as f:
                assert 'DOCUMENTATION' not in f.read()
            continue
        if 'requirements' in plugin_data:
            reqs = plugin_data['requirements']
            assert isinstance(reqs, list)
            for entry in reqs:
                add_req(req_data[collection], entry)
    line_ct += 1


with open('sniff_req/discovered.json', 'w') as f:
    json.dump(req_data, f, indent=2)

print(f'Inspected DOCUMENTATION for {line_ct} files.')
