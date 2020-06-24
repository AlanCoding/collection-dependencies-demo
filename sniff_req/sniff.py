import os
import sys
import importlib
import importlib.util
import yaml
import json


if len(sys.argv) == 1:
    raise Exception('Provide a target directory as argument.')


target = sys.argv[1]

if 'ansible_collections' in target:
    raise Exception('Your target directory is one level too deep.')


target_pythonpath = os.path.join(target, 'ansible_collections')


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
    for name in os.listdir(namespace_dir):
        collection_dir = os.path.join(namespace_dir, name)
        top_content = os.listdir(collection_dir)
        for lightbulb in a_ha_collection:
            if lightbulb in top_content:
                print(f'Found collection {namespace}.{name}')
                collections[f'{namespace}.{name}'] = []


sys.path.insert(0, os.path.join(os.getcwd(), target))


plugins_blacklist = (
    'terminal',  # frr
    'cliconf',
    'httpapi'  # arista.eos
)
plugin_ct = 0


for fqcn in collections.keys():
    namespace, name = fqcn.split('.')
    plugins_dir = os.path.join(target_pythonpath, namespace, name, 'plugins')
    # print(
    #     collection_dir + '   ' + str(
    #         [s for s in os.listdir(collection_dir) if not os.path.isdir(s)]
    #     )
    # )
    for plugin_type in os.listdir(plugins_dir):
        plugin_type_dir = os.path.join(plugins_dir, plugin_type)
        if not os.path.isdir(plugin_type_dir) or plugin_type in plugins_blacklist:
            continue
        print(f' sniffing {namespace}.{name}.{plugin_type}')
        for plugin_file in os.listdir(plugin_type_dir):
            if not plugin_file.endswith('.py') or plugin_file == '__init__.py':
                continue
            plugin, _ = plugin_file.rsplit('.')
            print(f'  sniffing {plugin_type}: {namespace}.{name}.{plugin}')
            plugin_ct += 1
            fq_import = f'ansible_collections.{namespace}.{name}.plugins.{plugin_type}.{plugin}'
            plugin_path = os.path.join(plugin_type_dir, plugin)

            try:
                # spec = importlib.util.spec_from_file_location(fq_import, plugin_path)
                # m = importlib.util.module_from_spec(spec)
                m = importlib.import_module(fq_import)
                has_doc = hasattr(m, 'DOCUMENTATION')
                is_yaml = False
                has_req = False
                if has_doc:
                    doc = m.DOCUMENTATION
                    try:
                        doc_dict = yaml.load(doc)
                        is_yaml = True
                        if 'requirements' in doc_dict:
                            reqs = doc_dict['requirements']
                            has_req = True
                            if not isinstance(reqs, list):
                                raise Exception(f'!! got requirements as non-list !! {reqs}')
                            for req in reqs:
                                if not isinstance(req, str):
                                    raise Exception('Entry in requirements not string')
                                if req not in collections[f'{namespace}.{name}']:
                                    collections[f'{namespace}.{name}'].append(req)
                    except Exception:
                        pass
                print(f'    documentation: {has_doc} {is_yaml} {has_req}')
            except (ImportError, ValueError) as e:
                print(f'  FAILED while sniffing {e}')
                failed.setdefault(f'{namespace}.{name}', [])
                if str(e) not in failed[f'{namespace}.{name}']:
                    failed[f'{namespace}.{name}'].append(str(e))
                # failed[f'{namespace}.{name}'].append(f'{plugin_type}.{plugin}')


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

