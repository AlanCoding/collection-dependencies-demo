import sys
import os
import importlib


target = sys.argv[1]  # needs to be absolute for this
fq_import = sys.argv[2]


sys.path.insert(0, target)

m = importlib.import_module(fq_import)

doc = getattr(m, "DOCUMENTATION", "")

print(doc)

