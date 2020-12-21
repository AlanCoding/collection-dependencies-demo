#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: import_collection_module
author: "Alan Rominger (@alancoding)"
short_description: Tests the import of Ansible modules.
description:
    - Tries to import each module given in list, give summary of outcome.
options:
    module_list:
      description:
        - List of modules to test the import of.
          This is a hacky thing, and will accept an absolute path string,
          or alternatively, the python module import.
      required: True
      default: []
      type: list
      elements: str
'''


from ansible.module_utils.basic import AnsibleModule
import os
import json


def main():
    argument_spec = dict(
        module_list=dict(type='list', elements='str', required=True)
    )
    module = AnsibleModule(argument_spec=argument_spec)

    module_list = module.params.get('module_list')

    good_deps = {}
    bad_deps = {}
    error_paths = []

    for module_thing in module_list:

        if module_thing.startswith('/'):
            if 'ansible_collections' not in module_thing:
                module.fail_json(msg='The path {} is not an Ansible collection path.'.format(module_thing))
            if not module_thing.endswith('.py'):
                module.fail_json(msg='The path {} is not a python file.'.format(module_thing))
            import_parts = module_thing.rsplit('.', 1)[0].split(os.path.sep)
            start_idx = import_parts.index('ansible_collections')
            import_string = '.'.join(import_parts[start_idx:-1])
        else:
            import_string = module_thing

        if len(import_string.split('.')) < 6:
            raise Exception('Bad value for module import string {}'.format(import_string))

        namespace, collection_name = import_string.split('.')[1:3]
        col_slug = '{}.{}'.format(namespace, collection_name)

        args = ['python3', '/alan/try_import.py', import_string]
        rc, out, err = module.run_command(args)

        failed = False
        if rc != 0:
            error_paths.append((import_string, out + err))
            failed = True
        else:
            try:
                data = json.loads(out.strip())
                for key, val in data.items():
                    if val is True:
                        good_deps.setdefault(col_slug, {})
                        good_deps[col_slug].setdefault(key, [])
                        good_deps[col_slug][key].append(import_string)
                    elif key.endswith('_EXC'):  # a common pattern of storing the exception
                        continue
                    else:
                        bad_deps.setdefault(col_slug, {})
                        bad_deps[col_slug].setdefault(key, [])
                        bad_deps[col_slug][key].append(import_string)
            except Exception as e:
                error_paths.append((import_string, 'Failed to parse JSON {}'.format(e)))
                failed = True

    module.exit_json(
        changed=False,
        failed=failed,
        good_deps=good_deps, bad_deps=bad_deps,
        error_paths=error_paths
    )


if __name__ == '__main__':
    main()
