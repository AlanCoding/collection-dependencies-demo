import os
import sys
import importlib
# import importlib.util
# import yaml
import subprocess
from ansible.parsing.utils.yaml import from_yaml
import json


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


sys.path.insert(0, os.path.join(os.getcwd(), target))
subp_env = os.environ.copy()
if 'PYTHONPATH' in os.environ:
    subp_env['PYTHONPATH'] = abs_target + ':' + os.environ['PYTHONPATH']
else:
    subp_env['PYTHONPATH'] = abs_target + ':'
# os.chdir(os.getcwd())


plugins_blacklist = (
    'terminal',  # frr
    'cliconf',
    'httpapi',  # arista.eos
    'action',  # ansible.netcommon parent action classes have problems
    'module_utils'
)
# bugs which I have filed errors about
error_exceptions = (
    "No module named 'ansible_collections.community.general.plugins.connection.kubectl'",
)
plugin_ct = 0


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
            plugin_path = os.path.join(plugin_type_dir, plugin)
            print(f'  sniffing {plugin_type}: {namespace}.{name}.{plugin} - {fq_import}')

            try:
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
                except Exception as e:
                    if 'collection metadata was not loaded' not in str(e):
                        raise
                    print('    falling back to import isolation because of error')
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
                print(f'    documentation: {has_doc} {is_yaml} {has_req}')
            except (ImportError, ValueError) as e:
                print(f'  FAILED while sniffing {fq_import}')
                failed.setdefault(fqcn, [])
                if str(e) not in failed[fqcn]:
                    failed[fqcn].append(str(e))
                # failed[fqcn].append(f'{plugin_type}.{plugin}')
                for text in error_exceptions:
                    if text not in str(e):
                        raise


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

