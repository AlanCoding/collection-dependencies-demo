### Collection that Depends on "Everything" from Galaxy

This is a genuine _installable_ collection that depends on a list of collections scraped from Ansible Galaxy.
For various reasons, this does not include literally every single collection.
Many collections are not installable, so one of the most time-consuming parts is identifying those.
Some are just so old that they are no longer compatible with the `ansible-galaxy` commands.
But in other cases, they do not install because they do not use X.Y.Z version.
In yet other cases, users wrote `galaxy.yml` that blows up the commands.

Expect installing this to _take a very long time_ unless you do so without deps.
If you have a folder with all the deps (the whole of Galaxy) pre-downloaded, you can and should reuse those.
Even with dependencies pre-installed, I find `make install_everything` takes about 50 seconds.

You can re-generate the list of collection names with `python everything/fetch.py`.
This also takes a very long time, but presumably these will change in the future.
The collections identified from that script are put in the `galaxy.yml` file for this collection.

#### Analysis

How many collections have a docs folder??
About 88, but several are internal to the same collection.

```
find everything/target -type d -name "docs" | wc -l
```

How large are the collections?? All of them are 226M when taken together.

```
du -sh all --max-depth=1
du -h -d1 everything/target/ansible_collections/ | sort -h
```

The 2nd command orders the collections in order of size.
Small collections take 16K of space.
The `awx.awx` collection as an example is in range of 300K.
Largest collections are like 10-40M.

#### Gripes about behavior

When doing the install with the `--force` command, it should not
download the dependencies again, but I think this indicates that it does.

```
Collection 'sundari_28.firstcoll' obtained from server default https://galaxy.ansible.com/api/
```

If a dependency is added and you use the install command, it will not
install those new dependencies.

In fact, it's kind of crazy that the install command will skip a collection
when you are giving it a .tar.gz file which is obviously a higher version
than the installed one. (need to replicate further)

Also, it doesn't seem to actually do dependency resolution:
(need to write this up in issue)

```
ERROR! Cannot meet dependency requirement 'debops.debops:1.1.4' for collection alancoding.deps from source 'https://galaxy.ansible.com/api/'. Available versions before last requirement added: 2.0.1
Requirements from:
	alancoding.everything - 'debops.debops:*'
	alancoding.deps - 'debops.debops:1.1.4'
```

The collection `softasap.swarm_box` also failed late in the process on install.

```
Installing 'softasap.swarm_box:0.0.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/all/target/ansible_collections/softasap/swarm_box'
Downloading https://galaxy.ansible.com/download/softasap-swarm_box-0.0.1.tar.gz to /Users/alancoding/.ansible/tmp/ansible-local-235553r_151kh/tmp3i7brcrh
ERROR! Collection tar at '/Users/alancoding/.ansible/tmp/ansible-local-235553r_151kh/tmp3i7brcrh/softasap-swarm_box-0.0.1.tar7rr8vcy9.gz' does not contain the expected file 'releases/softasap-swarm_box-0.0.1.tar.gz'.
```

Also fails way too late:

```
Installing 'lhoang2.beta_content:4.0.6' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/all/target/ansible_collections/lhoang2/beta_content'
Downloading https://galaxy.ansible.com/download/lhoang2-beta_content-4.0.6.tar.gz to /Users/alancoding/.ansible/tmp/ansible-local-24581tfa2mliq/tmp37a295wx
ERROR! Checksum mismatch for 'FILES.json' inside collection at '/Users/alancoding/.ansible/tmp/ansible-local-24581tfa2mliq/tmp37a295wx/lhoang2-beta_content-4.0.6.tar7opakxbd.gz'
```

```
Installing 'newswangerd.c1:1.0.1' to '/Users/alancoding/Documents/repos/collection-dependencies-demo/all/target/ansible_collections/newswangerd/c1'
Downloading https://galaxy.ansible.com/download/newswangerd-c1-1.0.1.tar.gz to /Users/alancoding/.ansible/tmp/ansible-local-25375fk3722kr/tmpwcrly2e5
ERROR! Checksum mismatch for 'MANIFEST.json' inside collection at '/Users/alancoding/.ansible/tmp/ansible-local-25375fk3722kr/tmpwcrly2e5/newswangerd-c1-1.0.1.tari3owxgi9.gz'
```



