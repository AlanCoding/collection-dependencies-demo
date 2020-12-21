#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


from ansible.module_utils.basic import AnsibleModule
import os
import glob


COLLECTION_PATHS = '/usr/share/ansible/collections'


def main():
    # for now, this takes no arguments
    module = AnsibleModule(argument_spec={})
    if not os.path.exists(COLLECTION_PATHS):
        module.fail_json(msg='Location {} does not exist'.format(COLLECTION_PATHS))

    module_pattern = os.path.join(
        COLLECTION_PATHS,
        'ansible_collections', '**', '*.py'
    )

    ret = []
    for path in glob.iglob(module_pattern, recursive=True):
        if path.endswith('__init__.py'):
            continue

        path_parts = path.rsplit('.', 1)[0].split(os.path.sep)
        start_idx = path_parts.index('ansible_collections')
        import_parts = path_parts[start_idx:]

        if len(import_parts) < 5:
            continue  # no plugins and type folder like plugins/modules, plugins/inventory
        if import_parts[3] != 'plugins':
            continue  # this analysis is only concerned with plugins
        # TODO: maybe figure out some more elegant way to handle this filter
        with open(path, 'r') as f:
            if 'HAS_' not in f.read():
                continue

        import_string = '.'.join(import_parts)

        ret.append(import_string)

    module.exit_json(
        changed=False,
        paths=ret
    )


if __name__ == '__main__':
    main()
