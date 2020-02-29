import os
import yaml


old_plugins = """aws_ec2
gcp_compute
vmware_vm_inventory
openstack
foreman
tower
ovirt4
ovirt
rhv
cloudforms""".split('\n')

exceptions = [
    'ovirt',
    'cloudforms'
]

HOME = '/Users/alancoding/Documents/repos'


bot_meta = '{}/ansible/.github/BOTMETA.yml'.format(HOME)
nwo = '{}/collection_migration/scenarios/nwo/'.format(HOME)


with open(bot_meta, 'r') as stream:
    bot_data = yaml.safe_load(stream)


inv_data = {}

for fn, data in bot_data['files'].items():
    if fn.startswith('$plugins/inventory/'):
        file_name = fn[len('$plugins/inventory/'):]
        if '.' not in file_name:
            base = file_name
        else:
            base, ext = file_name.split('.')
        if base in old_plugins:
            inv_data[fn] = data

print('')
print(' ----- data from the BOTMETA ----- ')
print('')

print(yaml.dump(inv_data, default_flow_style=False))

print('')
print('')
print(' ----- data from the NWO ----- ')
print('')

nwo_data = {}

for file_name in os.listdir(nwo):
    if not file_name.endswith('.yml'):
        continue
    with open(os.path.join(nwo, file_name), 'r') as stream:
        migration_data = yaml.safe_load(stream)
        for collection_name, data in migration_data.items():
            for plugin_file in data.get('inventory', []):
                if '.' not in plugin_file:
                    plugin_name = plugin_file
                else:
                    plugin_name, ext = plugin_file.split('.')
                if plugin_name in old_plugins:
                    summary_data = nwo_data.setdefault(file_name, [])
                    summary_data.append({
                        collection_name: plugin_name
                    })


print(yaml.dump(nwo_data, default_flow_style=False))


print('')
print('')
print(' ----- Exceptions ----- ')
print('')


print(yaml.dump(exceptions, default_flow_style=False))
