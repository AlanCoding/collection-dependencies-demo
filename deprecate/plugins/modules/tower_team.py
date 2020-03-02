#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2017, Wayne Witzel III <wayne@riotousliving.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['deprecated'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tower_team
author: "Wayne Witzel III (@wwitzel3)"
version_added: "2.3"
deprecated:
    removed_in: "3.7"
    why: Deprecated in favour of C(_import) module.
    alternative: foo
short_description: create, update, or destroy Ansible Tower team.
description:
    - Create, update, or destroy Ansible Tower teams. See
      U(https://www.ansible.com/tower) for an overview.
options:
    name:
      description:
        - Name to use for the team.
      required: True
      type: str
    description:
      description:
        - The description to use for the team.
      type: str
    organization:
      description:
        - Organization the team should be made a member of.
      required: True
      type: str
    state:
      description:
        - Desired state of the resource.
      choices: ["present", "absent"]
      default: "present"
      type: str
'''


EXAMPLES = '''
- name: Create tower team
  tower_team:
    name: Team Name
    description: Team Description
    organization: test-org
    state: present
    tower_config_file: "~/tower_cli.cfg"
'''

from ansible.module_utils.basic import AnsibleModule

try:
    import tower_cli
    import tower_cli.exceptions as exc
except ImportError:
    pass


def main():

    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        organization=dict(required=True),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get('name')
    description = module.params.get('description')
    organization = module.params.get('organization')
    state = module.params.get('state')

    json_output = {'team': name, 'state': state}

    team = tower_cli.get_resource('team')

    try:
        org_res = tower_cli.get_resource('organization')
        org = org_res.get(name=organization)

        if state == 'present':
            result = team.modify(name=name, organization=org['id'],
                                 description=description, create_on_missing=True)
            json_output['id'] = result['id']
        elif state == 'absent':
            result = team.delete(name=name, organization=org['id'])
    except (exc.NotFound) as excinfo:
        module.fail_json(msg='Failed to update team, organization not found: {0}'.format(excinfo), changed=False)
    except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
        module.fail_json(msg='Failed to update team: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)


if __name__ == '__main__':
    main()
