import os
import sys
import importlib
import yaml
import subprocess

from ansible.parsing.utils.yaml import from_yaml
from ansible.parsing.yaml.dumper import AnsibleDumper

import json
from ansible.plugins import loader


if len(sys.argv) == 1:
    raise Exception('Provide a target directory as argument.')


target = sys.argv[1]
abs_target = os.path.join(os.getcwd(), target)

if 'ansible_collections' in target:
    raise Exception('Your target directory is one level too deep.')


target_pythonpath = os.path.join(target, 'ansible_collections')
target_collection = None

if len(sys.argv) > 2:
    target_collection = sys.argv[2]


a_ha_collection = (
    'galaxy.yml',
    'galaxy.yaml',
    'MANIFEST.json',
    'FILES.json'
)


with open('sniff_req/spec_ex.yml', 'r') as f:
    ee_tmp_str = f.read()

print('Execution environment template:')
print(ee_tmp_str)

ee_tmp_dict = from_yaml(ee_tmp_str)
ee_tmp_dict['dependencies']['python'] = []
ee_tmp_dict['dependencies']['system'] = []
ee_tmp_dict['autogen'] = True

print('dumped')
results = yaml.dump(ee_tmp_dict, Dumper=AnsibleDumper, default_flow_style=False)
print(results)


collections = {}
failed = {}


for namespace in os.listdir(target_pythonpath):
    namespace_dir = os.path.join(target_pythonpath, namespace)
    local_reqs = []
    for name in os.listdir(namespace_dir):
        collection_dir = os.path.join(namespace_dir, name)
        top_content = os.listdir(collection_dir)
        for lightbulb in a_ha_collection:
            if lightbulb in top_content:
                print(f'Found collection {namespace}.{name}')
                collections[f'{namespace}.{name}'] = []
                break
        else:
            raise Exception(f'Path at {collection_dir} is not a collection')

for fqcn in collections.keys():
    if target_collection and fqcn != target_collection:
        continue
    namespace, name = fqcn.split('.')
    collection_dir = os.path.join(target_pythonpath, namespace, name)
    for candidate in os.listdir(collection_dir):
        if 'requirement' in candidate and 'txt' in candidate:
            with open(os.path.join(collection_dir, candidate), 'r') as f:
                req_text = f.read()
            req_text = req_text.strip()
            for line in req_text.split('\n'):
                if req_text not in collections[fqcn]:
                    collections[fqcn].append(line)


print()
sys.path.insert(0, abs_target)
subp_env = os.environ.copy()
if 'PYTHONPATH' in os.environ:
    subp_env['PYTHONPATH'] = abs_target + ':' + os.environ['PYTHONPATH']
else:
    subp_env['PYTHONPATH'] = abs_target + ':'
# os.chdir(os.getcwd())

os.environ['ANSIBLE_COLLECTIONS_PATH'] = abs_target


plugins_blacklist = (
    'terminal',  # frr
    'cliconf',
    'httpapi',  # arista.eos
    'action',  # ansible.netcommon parent action classes have problems
    'module_utils'  # rarely has DOCUMENTATION anyway
)
# these seem to be due to some suspicious stale __pycache__ dirs
error_exceptions = ()
# (
#     # azure/azcollection/plugins/modules/azure_rm_appgateway.py
#     "No module named 'ansible.module_utils.network'",
#     # google/cloud/plugins/modules/gcp_compute_target_https_proxy_info.py
#     "No module named 'ansible.module_utils.gcp_utils'"
# )
plugin_ct = 0


not_req_file = set((
    'README.md',
    'galaxy.yml',
    'plugins',
    'meta',
    'examples',
    'docs',
    '.git',
    '.github',
    '.gitignore',
    'COPYING',
    'tests',
    'test',
    'changelogs',
    'CODE_OF_CONDUCT.md',
    'Makefile',
    'LICENSE',
    'ansible.cfg',
    '.mailmap',
    '.yamllint',
    'CHANGELOG.rst',
    'README.rst',
    'playbooks',
    'Development.md',
    'misc',
    'CODE-OF-CONDUCT.md',
    'galaxy.yml.in',
    'SECURITY.md',
    'scripts',
    'CONTRIBUTING.md',
    'custom-cred-types',
    'ignore-2.9.txt',
    'CredScanSuppressions.json',
    'pr-pipelines.yml',
    'hacking',
    'CHANGELOG.md',
    'roles',
    '.changelog',
    '.ansible-lint',
    'molecule',
    'contrib',
    'codecov.yml',
    '.all-contributorsrc',
    'setup.cfg',
    'build.sh',
    'ovirt-ansible-collection.spec.in',
    'automation',
    'automation.yaml',
    'docker-compose.yml',
    'travis_run.sh',
    '.travis.yml',
    '.zuul.yaml',
    'LICENSE.txt',
    'releases',
    'MANIFEST.json',
    'tools',
    'azure-pipelines.yml',
    'shippable.yml'
    
))
req_files = {}


used_lookup = 0
used_import = 0
used_process = 0


for fqcn in collections.keys():
    namespace, name = fqcn.split('.')
    collection_dir = os.path.join(target_pythonpath, namespace, name)
    for candidate in os.listdir(collection_dir):
        if candidate not in not_req_file:
            req_files.setdefault(fqcn, [])
            req_files[fqcn].append(candidate)

print()
print('Candidate requirement files')
print(json.dumps(req_files, indent=2))


reverse_reqs = {}
for k, v in req_files.items():
    for f in v:
        reverse_reqs.setdefault(f, [])
        reverse_reqs[f].append(k)


print()
print('Pivoted requirements file')
print(json.dumps(reverse_reqs, indent=2))

print()
print('Total collections in set: {}'.format(len(collections)))
print('Total supported requirements {}'.format(len(
    set(reverse_reqs.get('requirements.txt', [])) | set(reverse_reqs.get('bindep.txt', []))
)))


for fqcn in collections.keys():
    if target_collection and fqcn != target_collection:
        continue
    namespace, name = fqcn.split('.')
    plugins_dir = os.path.join(target_pythonpath, namespace, name, 'plugins')
    for plugin_type in os.listdir(plugins_dir):
        plugin_type_dir = os.path.join(plugins_dir, plugin_type)
        if not os.path.isdir(plugin_type_dir) or plugin_type in plugins_blacklist:
            continue
        print(f' sniffing {namespace}.{name}.{plugin_type}')
        for plugin_file in os.listdir(plugin_type_dir):
            if not plugin_file.endswith('.py') or plugin_file == '__init__.py':
                continue
            plugin, _ = plugin_file.rsplit('.')
            plugin_ct += 1
            fq_import = f'ansible_collections.{namespace}.{name}.plugins.{plugin_type}.{plugin}'
            plugin_path = os.path.join(os.getcwd(), plugin_type_dir, plugin_file)
            print(f'  sniffing {plugin_type}: {namespace}.{name}.{plugin} - {fq_import}')

            try:
                excs = []
                try:
                    type_loader = getattr(loader, f'{plugin_type}_loader', None)
                    assert type_loader is not None
                    m = type_loader._load_module_source(
                        f'{namespace}.{name}.{plugin}',
                        plugin_path
                    )
                    if not hasattr(m, 'DOCUMENTATION'):
                        if hasattr(m, 'ModuleDocFragment'):
                            doc = ''
                            doc_frag = m.ModuleDocFragment
                            for thing in dir(doc_frag):
                                if thing.isupper():
                                    doc += getattr(doc_frag, thing)
                        else:
                            doc = ''
                    else:
                        doc = m.DOCUMENTATION.strip('\n')
                    used_lookup += 1

                except Exception as e1:
                    excs.append(e1)
                    print('   falling back python import because loader not available: {}'.format(str(e1)))
                    try:
                        m = importlib.import_module(fq_import)
                        if not hasattr(m, 'DOCUMENTATION'):
                            if hasattr(m, 'ModuleDocFragment'):
                                doc = ''
                                doc_frag = m.ModuleDocFragment
                                for thing in dir(doc_frag):
                                    if thing.isupper():
                                        doc += getattr(doc_frag, thing)
                            else:
                                doc = ''
                        else:
                            doc = m.DOCUMENTATION.strip('\n')
                        used_import += 1
                    except Exception as e2:
                        excs.append(e2)
                        # if 'collection metadata was not loaded' not in str(e):
                        #     raise
                        print('    falling back to import isolation because of error: {}'.format(e2))
                        # need import to be isolated
                        cmd = [
                            sys.executable,
                            os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                'look_at.py'
                            ),
                            abs_target,
                            fq_import
                        ]
                        out = subprocess.check_output(cmd, env=subp_env)
                        out = str(out, encoding='utf-8')
                        doc = str(out).strip('\n')
                        used_process += 1

                has_doc = bool(doc)

                doc = doc.strip('\n')

                is_yaml = False
                has_req = False
                if has_doc:
                    try:
                        doc_dict = from_yaml(doc)
                        # doc_dict = yaml.safe_load(doc)
                        if 'requirements' not in doc_dict and len(doc_dict) == 1:
                            doc_dict = list(doc_dict.values())[0]
                        is_yaml = True
                        if 'requirements' in doc_dict:
                            reqs = doc_dict['requirements']
                            has_req = True
                            if not isinstance(reqs, list):
                                raise Exception(f'!! got requirements as non-list !! {reqs}')
                            for req in reqs:
                                if not isinstance(req, str):
                                    raise Exception('Entry in requirements not string')
                                if req not in collections[fqcn]:
                                    collections[fqcn].append(req)
                    except Exception:
                        print()
                        print(' ---- Error parsing documentation ----')
                        print(doc)
                        print(' -------------------------------------')
                        raise
                # print(f'    documentation stats: {has_doc} {is_yaml} {has_req}')
            except Exception as e3:
                excs.append(e3)
                print(f'  FAILED while sniffing {fq_import}')
                failed.setdefault(fqcn, [])
                if any(str(e) not in str(failed[fqcn]) for e in excs[:2]):
                    failed[fqcn].extend([str(e) for e in excs])
                # failed[fqcn].append(f'{plugin_type}.{plugin}')
                passes = False
                for text in error_exceptions:
                    if any(text in str(e) for e in excs):
                        passes = True
                print()
                print('The collections we could not assess because import failed')
                print()
                print(json.dumps(failed, indent=2))
                print()
                if not passes:
                    raise

    ee_spec_path = os.path.join(
        target_pythonpath, namespace, name, 'meta/execution-environment.yml'
    )
    ee_tmp_dict['dependencies']['python'] = collections[fqcn]
    # assure meta directory exists
    meta_dir = os.path.join(
        target_pythonpath, namespace, name, 'meta'
    )
    if not os.path.exists(meta_dir):
        os.makedirs(meta_dir)
    if os.path.exists(ee_spec_path):
        with open(ee_spec_path, 'r') as f:
            current_ee = f.read()
        current_ee_dict = from_yaml(current_ee)
    else:
        current_ee_dict = {'autogen': True}
    results = yaml.dump(ee_tmp_dict, Dumper=AnsibleDumper, default_flow_style=False)
    # only re-generate file if it has not been modified, use flag for this
    if 'autogen' in current_ee_dict:
        with open(ee_spec_path, 'w') as f:
            f.write(results)


print()
print(f'Ways imports were done: {used_lookup} {used_import} {used_process}')
print()


print()
print(f'Inspected total of {plugin_ct} plugins')
print()

print('At last, what we were looking for')
print('The unique requirements for each collection')
print()
print(json.dumps(collections, indent=2))

print()
print('The collections we could not assess because import failed')
print()
print(json.dumps(failed, indent=2))
