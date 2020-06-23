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
```

Then source the file it creates

```
source cloner/requirements.sh
```

takes about 7 seconds

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
