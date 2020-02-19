BUNDLE=$(shell ls -1at deps/alancoding-deps-*.tar.gz | head -1)
ALL_BUNDLE=$(shell ls -1at all/alancoding-everything-*.tar.gz | head -1)

build_deps:
	rm -rf deps/alancoding-deps-*.tar.gz
	ansible-galaxy collection build deps --output-path=deps -vvv

install_deps:
	ANSIBLE_COLLECTIONS_PATHS=deps/target ansible-galaxy collection install $(BUNDLE) -f -p deps/target -vvv

build_all:
	rm -rf all/alancoding-everything-*.tar.gz
	ansible-galaxy collection build all --output-path=all -vvv

just_install_all:
	ANSIBLE_COLLECTIONS_PATHS=all/target ansible-galaxy collection install $(ALL_BUNDLE) -f -p all/target -vvv

install_all_requirements:
	ANSIBLE_COLLECTIONS_PATHS=all/target ansible-galaxy collection install -r all/output.yml -p all/target -vvv

list_all:
	ANSIBLE_COLLECTIONS_PATHS=all/target ansible-galaxy collection list

repro_bug:
	# rm -rf bug_debops/target
	rm -rf bug_debops/alancoding-bug-0.0.1.tar.gz
	ansible-galaxy collection build bug_debops --output-path=bug_debops -vvv
	ANSIBLE_COLLECTIONS_PATHS=bug_debops/target ansible-galaxy collection install bug_debops/alancoding-bug-0.0.1.tar.gz -f -p bug_debops/target -vvv

# # this would take like 2 hours to run, so commenting out
# install_all:
# 	rm -rf all/target
# 	make just_install_all
