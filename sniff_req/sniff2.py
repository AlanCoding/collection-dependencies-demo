import sys
import os
import json
import ast

from ansible.parsing.plugin_docs import read_docstring
from ansible.parsing.yaml.loader import AnsibleLoader
from ansible import __version__


line_ct = 0


excludes = (
    # genuinely bad yaml, the command gives error:
    # ansible-doc google.cloud.gcp_pubsub_subscription
    'google/cloud/plugins/modules/gcp_pubsub_subscription.py',
)
validated_paths = set()
req_data = {}


EXCLUDE_REQUIREMENTS = (
    'ansible',
    'ansible-base',
    'python', 'Python',
    'yaml', 'PyYAML',
    'six.moves.StringIO', 'sys',
    '',
    'tox', 'pycodestyle', 'yamllint', 'voluptuous', 'pylint',
    'flake8', 'pytest', 'pytest-xdist', 'coverage', 'mock',
    'requests'
)


def pkg(req):
    p = None
    for sep in ('==', '>=', '>', '<', '<='):
        if sep in req:
            new_p = req.split(sep, 1)[0].strip()
            # If one of these occurs earlier than others, use that
            if p is None or len(new_p) < len(p):
                p = new_p
    if p is not None:
        return p
    return req


def exclude_req(req):
    if req.startswith('-r '):
        return True
    if pkg(req) in EXCLUDE_REQUIREMENTS:
        return True
    return False


def add_req(alist, req):
    if req in alist or exclude_req(req):
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
        # TODO: okay, yes, it is pointless to list these up,
        # I will give up the goal of validation of the doc_fragment sub-keys...
        # but not today
        assert key in (
            'DOCUMENTATION',
            'ONTAP',  # deprecated
            'NA_ONTAP', 'SOLIDFIRE', 'AWSCVS',  # netapp
            'FA',  # flash array
            'FB',  # flashblade
            # foreman
            'NESTED_PARAMETERS', 'OS_FAMILY', 'TAXONOMY', 'ENTITY_STATE',
            'ENTITY_STATE_WITH_DEFAULTS', 'HOST_OPTIONS', 'ORGANIZATION',
            'SCAP_DATASTREAM',
            'VALIDATEETAG', 'FACTSPARAMS',  # oneview in community.general
            'DOCKER_PY_1_DOCUMENTATION', 'DOCKER_PY_2_DOCUMENTATION',
            'EMC_VNX',  # emc in community.general
            'VX100',  # vexata
            'OPENSTACK',
            'PROVIDER', 'TRANSITIONAL_PROVIDER', 'STATE', 'RULEBASE',
            'VSYS_DG', 'DEVICE_GROUP', 'VSYS_IMPORT', 'VSYS', 'TEMPLATE_ONLY',
            'FULL_TEMPLATE_SUPPORT',  # panos
            'VCENTER_DOCUMENTATION'
        ), (key, path)
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
            if 'requirement' in candidate and 'txt' in candidate:
                with open(os.path.join(collection_dir, candidate), 'r') as f:
                    req_text = f.read()
                req_text = req_text.strip()
                for line in req_text.split('\n'):
                    add_req(req_data[fqcn], line)


for line in sys.stdin:
    line_ct += line.count('\n')
    for subline in line.split('\n'):
        if not subline:
            continue
        path, doc_line = subline.split(':', 1)
        path = path.replace('//', '/')  # special to grep
        path_parts = path.split(os.path.sep)
        if path_parts[4] in ('tests', 'scripts'):
            continue
        if len(path_parts) != 7:
            # identifies nested modules
            if path_parts[5] != 'modules':
                # should only apply for
                # f5networks/f5_modules/f5_modules_source/devtools/stubs/library_module.py
                print('Skipping {} because not a real module'.format(path))
                continue
        if path in validated_paths:
            # References to DOCUMENTATION later in the file should not re-add that file
            continue
        assert path_parts[1] == 'ansible_collections', path_parts
        namespace = path_parts[2]
        name = path_parts[3]

        collection = '{}.{}'.format(namespace, name)
        req_data.setdefault(collection, [])

        if any(path.endswith(exclude) for exclude in excludes):
            continue
        assert os.path.exists(path)
        validated_paths.add(path)

        if path_parts[5] == 'doc_fragments':
            fragments = ast_fragment_parse(path)
            check_requirements = list(fragments.values())
        else:
            plugin_data = read_docstring(path, verbose=False)['doc']
            check_requirements = [plugin_data]
        # print(json.dumps(read_docstring(path, verbose=False), indent=2))
        for plugin_data in check_requirements:
            if plugin_data is None:
                print(path)
                raise Exception('alan!')
            if 'requirements' in plugin_data:
                reqs = plugin_data['requirements']
                assert isinstance(reqs, list)
                for entry in reqs:
                    add_req(req_data[collection], entry)


with open('sniff_req/discovered.json', 'w') as f:
    json.dump(req_data, f, indent=2)

print(f'Inspected DOCUMENTATION for {line_ct} files.')
