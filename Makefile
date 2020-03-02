BUNDLE=$(shell ls -1at deps/alancoding-deps-*.tar.gz | head -1)
EVERYTHING_BUNDLE=$(shell ls -1at everything/alancoding-everything-*.tar.gz | head -1)

build_deps:
	rm -rf deps/alancoding-deps-*.tar.gz
	ansible-galaxy collection build deps --output-path=deps -vvv

install_deps:
	ANSIBLE_COLLECTIONS_PATHS=deps/target ansible-galaxy collection install $(BUNDLE) -f -p deps/target -vvv

build_everything:
	rm -rf everything/alancoding-everything-*.tar.gz
	ansible-galaxy collection build everything --output-path=everything -vvv

install_everything:
	ANSIBLE_COLLECTIONS_PATHS=everything/target ansible-galaxy collection install $(EVERYTHING_BUNDLE) -f -p everything/target -vvv

# this is separate because it's less atomic than the collection install
install_everything_requirements:
	ANSIBLE_COLLECTIONS_PATHS=everything/target ansible-galaxy collection install -r everything/output.yml -p everything/target -vvv

list_everything:
	ANSIBLE_COLLECTIONS_PATHS=everything/target ansible-galaxy collection list

repro_bug:
	# rm -rf bug_debops/target
	rm -rf bug_debops/alancoding-bug-0.0.1.tar.gz
	ansible-galaxy collection build bug_debops --output-path=bug_debops -vvv
	ANSIBLE_COLLECTIONS_PATHS=bug_debops/target ansible-galaxy collection install bug_debops/alancoding-bug-0.0.1.tar.gz -f -p bug_debops/target -vvv

# # this would take like 2 hours to run, so commenting out
# install_everything:
# 	rm -rf everything/target
# 	make just_install_everything

build_deprecate:
	rm -rf deprecate/alancoding-deprecate-*.tar.gz
	rm -rf deprecate/target
	ansible-galaxy collection build deprecate --output-path=deprecate -vvv

install_deprecate:
	ANSIBLE_COLLECTIONS_PATHS=deprecate/target ansible-galaxy collection install deprecate/alancoding-deprecate-1.0.0.tar.gz -f -p deprecate/target -vvv

sanity_deprecate: build_deprecate install_deprecate
	cd deprecate/target/ansible_collections/alancoding/deprecate && git init && git add .
	cd deprecate/target/ansible_collections/alancoding/deprecate && ansible-test sanity

build_awx_deps:
	git submodule foreach git clean -f
	cd awx/community.general && ansible-galaxy collection build  # required by Amazon
	cd awx/community.netcommon && ansible-galaxy collection build  # required by Amazon
	cd awx/ansible.amazon && ansible-galaxy collection build
	cd awx/community.vmware && ansible-galaxy collection build
	rm -rf awx/openstack.cloud/galaxy.yml
	cp awx/openstack.cloud/galaxy.yml.in awx/openstack.cloud/galaxy.yml
	cd awx/openstack.cloud && ansible-galaxy collection build
	cd awx/theforeman.foreman && ansible-galaxy collection build

install_awx_deps:  # run build_awx_deps before running this
	ANSIBLE_COLLECTIONS_PATHS=awx/target ansible-galaxy collection install $(shell ls -1at awx/ansible.amazon/ansible-amazon-*.tar.gz | head -1)

