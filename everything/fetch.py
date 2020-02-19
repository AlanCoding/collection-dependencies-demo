import requests


next_link = 'https://galaxy.ansible.com/api/v2/collections/'

while next_link:
    r = requests.get(next_link)
    assert r.status_code == 200
    data = r.json()
    for entry in data['results']:
        print('{}.{}'.format(entry['namespace']['name'], entry['name']))
    next_link = 'https://galaxy.ansible.com{}'.format(data['next'])
