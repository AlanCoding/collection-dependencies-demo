from graphviz import Digraph

import os
import sys

import json


BASE_DIR = os.path.join(os.path.dirname(__file__), 'target', 'ansible_collections')


dot = Digraph(
    format='svg',
    comment='Collection dependency graph'
)
dot.graph_attr['rankdir'] = 'LR'


for namespace in os.listdir(BASE_DIR):
    if namespace.startswith('.'):
        continue
    namespace_dir = os.path.join(BASE_DIR, namespace)
    for name in os.listdir(namespace_dir):
        id = '{}.{}'.format(namespace, name)
        dot.node(id, id)

for namespace in os.listdir(BASE_DIR):
    if namespace.startswith('.'):
        continue
    namespace_dir = os.path.join(BASE_DIR, namespace)
    for name in os.listdir(namespace_dir):
        if name.startswith('.'):
            continue
        id = '{}.{}'.format(namespace, name)
        manifest_file = os.path.join(namespace_dir, name, 'MANIFEST.json')
        with open(manifest_file) as f:
            data = json.load(f)
        if len(sys.argv) > 1:
            key = sys.argv[1]
            value = data['collection_info'][key]
            if not value:
                continue
            if namespace == 'alancoding' and name =='everything':
                continue
            print(id + '   ' + str(value))

        # dot.edge(id, id)
        # 
        # for node in nodes:
        #     dot.node(node, node)
        # for r, p in edges:
        #     dot.edge(r, p)
        # 
        # print(dot.source)
        # dot.render(file, view=False)
