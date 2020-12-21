### Execution Environment Import Tester

The playbook and modules here are an attempt to slap together a POC for
diagnosing the completeness of execution environments.

#### Background and Definitions

Ansible collections are, by definition, a collection of Ansible plugins
and some other stuff like roles.
For our purposes, we only care about plugins.
There are around a dozen types of Ansible plugins, for the exact list
see the `-t` option in `ansible-doc --help`.

Our of the Ansible plugin types, we can divide them into 2 categories:

 - plugins that run on the control machine (ex: `inventory`, `lookup`)
 - plugins that run on the remote machine (ex: `module`)

If a plugin runs on the remote machine, it may still be ran on the controller
via `delegate_to`, or something like that.

Execution environments are container images used for the Ansible controller.
The canonical way of building execution environments is by `ansible-builder`.

Collections have the option of adding metadata about their requirements,
so that `ansible-builder` will install those dependencies automatically
in an execution environment that includes that collection.

If a collection does not add metadata about requirements, then its content
can still be used, but many that require an external dependency will error.
See `ansible.base` and `community.general` for two obvious examples of this.
An execution environment that includes that content is intentionally incomplete,
in that dependencies for all controller or remote actions are not present.

#### Objectives

It is ambiguous whether an execution environment should have dependencies for
remote plugins installed. If managing other machines (as opposed to itself)
the playbook or role running may install those dependencies as a separate task.
Many of these are highly platform-specific. For example, the remote machine
may be windows, so dependencies of windows modules are obviously inapplicable
to a controller.

Controller plugins, on the other hand, are probably useless without their
applicable dependencies installed.

The `runner` user inside execution environments does not have permission to
install software. So if dependencies are not satisfied through
execution environment metadata, then the only other good option is to
install them through customization of the image.

This tool primarily seeks to catalog what controller-side dependencies
are expected, but absent, from the image.

#### Requirement Identification

The most comprehensive way to identify dependencies is to see the documentation
of plugins. See, within this project, `sniff_req/discovered.json` for an
attempt to aggregate all the declared `requirements:` from plugin doc_fragments.

Documentation, however, is intended for human consumption. Options for
machine-readable categorization of Ansible requirements are poor.
Thus, the python `ast` module is used here as the best-available option.

This logic seeks to identify a common code pattern:

```
try:
   from xxx import xxx
   HAS_xxx = True
except xxx:
   HAS_xxx = False
```

A painful lesson I learned from prior work sniffing requirements is that
imports require code isolation.

The code isolation requirement lends itself to a playbook solution with
separation of responsibilities into tasks.

 - First task (or set of tasks) identifies importable modules
 - Second task imports those modules and seeks to find `HAS_` variables

It is a speculative check, but identifying `HAS_` variables that resolve
to `False` on import will suggest that a dependency is missing, and thus
could be resolved by adding that dependency to the execution environment
metadata.
