import requests
import yaml
import sys
import time
import os


source_file = sys.argv[1]
start_time = time.time()
last_time = start_time

def print_time():
    global last_time
    now = time.time()
    total_delta = now - start_time
    delta = now - last_time
    last_time = now
    print(f'  {total_delta} - {delta}')

with open(source_file, 'r') as f:
    source_data = yaml.safe_load(f)


import json
print(json.dumps(source_data, indent=2))


clones = []


for col_data in source_data['collections']:
    print_time()
    name = col_data['name']
    namespace, col_name = name.split('.')
    http_name = name.replace('.', '/')
    r = requests.get(f'https://galaxy.ansible.com/api/v2/collections/{http_name}/')
    print_time()
    print()
    print(name)
    # print(r.json())
    version_url = r.json()['latest_version']['href']
    r = requests.get(version_url)
    # print(r.json())
    repo = None
    metadata = r.json()['metadata']
    for key in ('homepage', 'repository', 'issues',):
        candidate = metadata[key]
        print('  ' + str(candidate))
        if candidate.startswith('https://github.com'):
            repo = candidate
            break
        elif candidate.startswith('http://github.com'):
            repo = 'https' + candidate[len('http'):]
            break
        elif candidate.endswith('.git'):
            repo = candidate[:-len('.git')]
            break
    if repo is None:
        print(f'Could not find repo for {http_name}')
    else:
        clones.append(f'rm -rf ~/.ansible/collections/ansible_collections/{namespace}/{col_name}/')
        clones.append(f'mkdir -p ~/.ansible/collections/ansible_collections/{namespace}')
        clones.append(f'git clone {repo}.git ~/.ansible/collections/ansible_collections/{namespace}/{col_name}')

dest_path = os.path.join(os.path.dirname(__file__), 'requirements.sh')

with open(dest_path, 'w') as f:
    f.write('\n'.join(clones))

print('--------')
print('\n'.join(clones))

# next_link = 'https://galaxy.ansible.com/api/v2/collections/'
# 
# while next_link:
#     r = requests.get(next_link)
#     assert r.status_code == 200
#     data = r.json()
#     for entry in data['results']:
#         print('{}.{}'.format(entry['namespace']['name'], entry['name']))
#     next_link = 'https://galaxy.ansible.com{}'.format(data['next'])

