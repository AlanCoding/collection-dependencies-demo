### Examples of SCM requirement files

This tests Ansible / Ansible Galaxy requirements that have source control
sources inside of them. This was enabled for collections with the PR:

https://github.com/ansible/ansible/pull/69154

Example of testing these:

```
ANSIBLE_COLLECTIONS_PATH=scm_requirements/target/ ansible-galaxy collection install -r scm_requirements/collection_requirements.yml -p scm_requirements/target
```

Does installing this way pull in the `.git` folder and all the git information?

no.

