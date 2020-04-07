### How do I rewrite my roles for collections?

example content:

(run from top level of repo)

```
ansible-playbook role_compat/as_playbook.yml
```

this example works in Ansible 2.7-2.9, but will not work in Ansible 2.10

role example:

```
ansible-playbook role_compat/as_role.yml
```

This will work in Ansible 2.10, but not Ansible 2.7, with error:

```
ERROR! 'collections' is not a valid attribute for a RoleMetadata

The error appears to have been in '/Users/alancoding/Documents/repos/collection-dependencies-demo/role_compat/roles/my_hg/meta/main.yml': line 1, column 1, but may
be elsewhere in the file depending on the exact syntax problem.

The offending line appears to be:


collections:
^ here
```

#### Uninstalled collection

```
ansible-playbook role_compat/missing_collection.yml
```

This shows that if a collection is listed under `collections:`, and this
collection is not actually installed, then it will run anyway.

It will not even give a warning.
