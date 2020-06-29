### Examples of SCM requirement files

This tests Ansible / Ansible Galaxy requirements that have source control
sources inside of them. This was enabled for collections with the PR:

https://github.com/ansible/ansible/pull/69154

Example of testing these:

```
ANSIBLE_COLLECTIONS_PATH=scm_requirements/target/ ansible-galaxy collection install -r scm_requirements/collection_requirements.yml -p scm_requirements/target
```

### Answering Questions about Behavior

#### Installed Content of Primary Dependencies

Does installing this way pull in the `.git` folder and all the git information?

no.

Okay, well then what _is_ installed?

```
$ ls scm_requirements/target/ansible_collections/amazon/aws
COPYING		FILES.json	MANIFEST.json	README.md	meta		plugins		shippable.yml	tests
```

This is an SCM requirement, and there's no `galaxy.yml` file.

Nonetheless, this does not pass

```
$ ANSIBLE_COLLECTIONS_PATH=scm_requirements/target/ ansible-galaxy collection verify amazon.aws:1.0.0
[WARNING]: You are running the development version of Ansible. You should only run Ansible from "devel" if you are modifying the Ansible engine, or trying out features under
development. This is a rapidly changing source of code and can become unstable at any point.
Collection amazon.aws contains modified content in the following files:
amazon.aws
    MANIFEST.json
    FILES.json
```

to do a diff..

```
$ diff scm_requirements/target/ansible_collections/amazon/aws/MANIFEST.json ~/.ansible/collections/ansible_collections/amazon/aws/MANIFEST.json 
30c30
<   "chksum_sha256": "70d00a80bf77e40333627bebbebf6e3a749a1adb11ca843c5a85e6e95759573c",
---
>   "chksum_sha256": "415b9817b1eb2e6fee323e0324c7f9307c512ac5203630e37dcc561016eb4179",
```

The `FILES.json` data seems to have mismatches in both checksums and in real content.
This could be because changes are made before the official build
but even without such changes, I do not expect that a re-build will pass the
verify command. This may be by design.

#### Sourcing Content for Secondary Dependencies

See the example of `community.mongodb` in the collection requirements example.

```
$ ls scm_requirements/target/ansible_collections/community/general/*.json scm_requirements/target/ansible_collections/community/general/*.yml
scm_requirements/target/ansible_collections/community/general/FILES.json	scm_requirements/target/ansible_collections/community/general/shippable.yml
scm_requirements/target/ansible_collections/community/general/MANIFEST.json

$ ls scm_requirements/target/ansible_collections/community/mongodb/*.json scm_requirements/target/ansible_collections/community/mongodb/*.yml
ls: scm_requirements/target/ansible_collections/community/mongodb/*.yml: No such file or directory
scm_requirements/target/ansible_collections/community/mongodb/FILES.json	scm_requirements/target/ansible_collections/community/mongodb/MANIFEST.json
```

