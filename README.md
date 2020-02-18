### Ansible collection dependencies

This is an example of a collection that has dependencies. How to use:

```
make build
make install
```

The install target will install it in a directory `target/`

That is for the default test case, other cases will be in subfolders.

#### What you should see

Output from the install command:

```
$ make install
rm -rf target
ANSIBLE_COLLECTIONS_PATHS=target ansible-galaxy collection install alancoding-deps-1.0.1.tar.gz -p target
Process install dependency map
Starting collection install process
Installing 'alancoding.deps:1.0.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/alancoding/deps'
Installing 'alancoding.basic:0.0.5' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/alancoding/basic'
Installing 'awx.awx:9.1.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/awx/awx'
Installing 'devoperate.base:0.1.0' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/devoperate/base'
Installing 'crivetimihai.workstation:1.0.12' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/crivetimihai/workstation'
Installing 'dynatrace_innovationlab.collection:1.0.0' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/dynatrace_innovationlab/collection'
Installing 'ganeshrn.test:1.0.0' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/ganeshrn/test'
Installing 'debops.debops:1.1.4' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/debops/debops'
Installing 'cjsteel.development_environment:1.2.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/cjsteel/development_environment'
Installing 'xlab_si.sesame:1.0.0' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/xlab_si/sesame'
```

You can see it installs a lot!

Inspect the info about this (empty) collection:

```
$ cat target/ansible_collections/alancoding/deps/MANIFEST.json 
{
 "collection_info": {
  "namespace": "alancoding",
  "name": "deps",
  "version": "1.0.1",
  "authors": [
   "your name <example@domain.com>"
  ],
  "readme": "README.md",
  "tags": [],
  "description": "your collection description",
  "license": [
   "GPL-2.0-or-later"
  ],
  "license_file": null,
  "dependencies": {
   "alancoding.basic": "0.0.5",
   "awx.awx": ">=8.0.0",
   "devoperate.base": "0.1.0",
   "crivetimihai.workstation": "1.0.12",
   "dynatrace_innovationlab.collection": "1.0.0",
   "ganeshrn.test": "1.0.0",
   "debops.debops": "1.1.4",
   "cjsteel.development_environment": "1.2.1",
   "xlab_si.sesame": "1.0.0"
  },
  "repository": "http://example.com/repository",
  "documentation": "http://docs.example.com",
  "homepage": "http://example.com",
  "issues": "http://example.com/issue/tracker"
 },
 "file_manifest_file": {
  "name": "FILES.json",
  "ftype": "file",
  "chksum_type": "sha256",
  "chksum_sha256": "ba62c5eb1c19e664da1554e22abcae5af41ba971c76c063eb8202cccc849dcc6",
  "format": 1
 },
 "format": 1
}
```

#### Only Installing One

This target only deletes this collection without also deleting its dependencies.

```
$ make install_one
rm -rf target/ansible_collections/alancoding/deps/
make just_install
ANSIBLE_COLLECTIONS_PATHS=target ansible-galaxy collection install alancoding-deps-1.0.1.tar.gz -p target
Process install dependency map
Starting collection install process
Installing 'alancoding.deps:1.0.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/target/ansible_collections/alancoding/deps'
Skipping 'alancoding.basic' as it is already installed
Skipping 'awx.awx' as it is already installed
Skipping 'devoperate.base' as it is already installed
Skipping 'crivetimihai.workstation' as it is already installed
Skipping 'dynatrace_innovationlab.collection' as it is already installed
Skipping 'ganeshrn.test' as it is already installed
Skipping 'debops.debops' as it is already installed
Skipping 'cjsteel.development_environment' as it is already installed
Skipping 'xlab_si.sesame' as it is already installed
```

#### Ignored Files

With this build process, it would get recursive with file ignores.
That's because everything is put into `target/`, and before a certain
Ansible version, everything on this folder level would get included
in the `.tar.gz` file.. including the `.tar.gz` file.
In this case, that means the file includes the old build of itself
and install of its dependencies. Clearly not good. Cleaner current state is:

```
$ ls target/ansible_collections/alancoding/deps/
FILES.json	MANIFEST.json
```

Empty collection is empty!
