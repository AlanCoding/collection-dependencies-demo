import sys
import os
import json

from ansible.plugins import loader

import importlib


import_string = sys.argv[-1]


if not import_string.startswith('ansible_collections.'):
    raise Exception('This script expects a collection FQCN iport, got {}'.format(import_string))


# ex: ansible_collections.community.general.plugins.modules.ohai
col_folder, namespace, name, plugin_folder, plugin_type, plugin_path = import_string.split('.', 5)

if plugin_folder != 'plugins':
    raise Exception('Expected to get location in the plugins module of collection, got: {}'.format(import_string))



for collection_home in ('/usr/share/ansible/collections', '~/.ansible/collections'):
    file_path = os.path.expanduser(os.path.join(
        collection_home, col_folder, namespace, name, plugin_folder, plugin_type, *plugin_path.split('.')
    ) + '.py')
    if os.path.exists(file_path):
        break
else:
    raise RuntimeError('A python file at expected locations does not exist.')


# if plugin_type == 'modules':
#     type_loader = loader.module_loader
# elif plugin_type == 'doc_fragments':
#     type_loader = loader.fragment_loader
# else:
#     type_loader = getattr(loader, f'{plugin_type}_loader', None)
#
# assert type_loader is not None


# py_module = type_loader._load_module_source(
#     f'{namespace}.{name}.{plugin_folder}',
#     file_path
# )

# FIXME: this is not the recommended way of importing, but is more robust
py_module = importlib.import_module(import_string)

result = {}

for attr in dir(py_module):
    if attr.startswith('HAS_'):
        val = getattr(py_module, attr)
        result[attr] = val

print(json.dumps(result, indent=2))
