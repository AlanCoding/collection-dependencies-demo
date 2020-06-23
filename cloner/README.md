### Clone from source tool

The idea here is to take a `requirements.yml` file for collections
and then do an "install" of it via direct clones of the source for each
of the collections.

This will rely on some assumptions about how the maintainers
structure their code.

### How to use

First, create a new `requirements.sh` file.

```
python cloner/get_sources.py cloner/awx.yml target
python cloner/get_sources.py cloner/acd.yml target
```

Then source the file it creates

```
source cloner/requirements.sh
```

takes about 7 seconds for AWX requirements (after expansion).

Doing the same for the ACD set takes 1 min and 14 seconds.

#### ACD fixes

Hit this on first attempt:

```
Cloning into 'target/ansible_collections/community/azure'...
fatal: unable to access 'https://github.com:ansible-collections/community..azure.git/': URL using bad/illegal format or missing URL
Cloning into 'target/ansible_collections/community/crypto'...
fatal: unable to access 'https://github.com:ansible-collections/community.crypto.git/': URL using bad/illegal format or missing URL
Cloning into 'target/ansible_collections/community/general'...
```

Triaged fix to be upstream https://github.com/ansible-collections/community.azure/pull/3

#### Tool special cases

Also hit issue

```
Cloning into 'target/ansible_collections/fortinet/fortimanager'...
fatal: repository 'https://github.com/fortinet-ansible-dev/ansible-galaxy-fortimanager-collection/tree/galaxy/1.0.3.git/' not found
Cloning into 'target/ansible_collections/fortinet/fortios'...
fatal: repository 'https://github.com/fortinet-ansible-dev/ansible-galaxy-fortios-collection/tree/fos_v6.0.0/galaxy_1.0.13.git/' not found
Cloning into 'target/ansible_collections/frr/frr'...
```

This was determined to be local.

### Reference use

The normal way to do this the same thing would be:

```
ansible-galaxy collection install --force -r cloner/requirements.yml -p target
```

But this gives older (released) snapshots, and sometimes you
want the development version.

This takes roughly 2 minutes to complete, which is over an order
of magnitude longer than the purely offline commands.

### Downloading and THEN installing

This is a new feature, so compare:

```
ansible-galaxy collection download -r cloner/awx.yml -p cloner/download/
```

takes about 2.5 minutes

```
ansible-galaxy collection install --force cloner/download/*.tar.gz
```

takes about 5 seconds
(note that this was all before the full set of AWX requirements)
