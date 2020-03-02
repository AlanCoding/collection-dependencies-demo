### Deprecation of Modules in a Collection

This is an example of a collection that hosts a deprecated module.
It also passes the sanity tests.

Original issue is described here:

https://github.com/ansible/ansible/issues/60424

The old style of deprecation with a leading `_` in the module name
does not work anymore.

An example of the new style is found at:

https://github.com/ansible-collections/ansible.amazon/blob/master/meta/routing.yml

run the sanity tests for this:

```
make sanity_deprecate
```

Can't remove `why` or `removed_in` due to failure

```
ERROR! Unexpected Exception, this is probably a bug: 'removed_in'
```

Removing alternative gives

```
ERROR! Unexpected Exception, this is probably a bug: 'alternative'
```

Putting all 3 of these keys in gives

```
ERROR: plugins/modules/tower_team.py:0:0: invalid-documentation: DOCUMENTATION.deprecated: extra keys not allowed @ data['deprecated']. Got {'removed_in': '3.7', 'why': 'Deprecated in favour of C(_import) module.', 'alternative': 'foo'}
```

And this is just the issue:

```
ERROR: plugins/modules/tower_team.py:0:0: deprecation-mismatch: Module deprecation/removed must agree in Metadata, by prepending filename with "_", and setting DOCUMENTATION.deprecated for deprecation or by removing all documentation for removed
```

