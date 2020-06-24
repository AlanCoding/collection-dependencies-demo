### Sniff requirements from collections

This tool is to build out data for what requirements different collections
have. It is ultimately intended to go into `ansible-builder` but only
to be ran once / initially as a means of bootstrapping all the metadata
for the collections out in the wild.

https://github.com/ansible/ansible-builder

### How to use

You need a folder which has collections in it. This could be `~/.ansible/collections`.
Other tools here are good for producing such folders with different reference
collection sets. See `cloner` for AWX deps & ACD, and `everything` if you're looking
to have a very bad time.

Take that folder and throw it into the script.

```
brew install libvirt  # only macos
pip install boto3 botocore linode_api4 libvirt-python pymongo
python sniff_req.py target
```

The pip installs are because some modules will error on import without libraries.
Not all plugins will be sniffed, due to unidentified bugs.
This script takes about 1 minute to do.
