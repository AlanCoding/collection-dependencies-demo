import sys
import os
import importlib


target = sys.argv[1]  # needs to be absolute for this
fq_import = sys.argv[2]


sys.path.insert(0, target)

m = importlib.import_module(fq_import)

doc = getattr(m, "DOCUMENTATION", "")

if hasattr(m, 'ModuleDocFragment'):
    doc = ''
    doc_frag = m.ModuleDocFragment
    for thing in dir(doc_frag):
        if thing.isupper():
            doc += getattr(doc_frag, thing)


print(doc)

