BUNDLE=$(shell ls alancoding-deps-*.tar.gz | tail -1)
ALL_BUNDLE=$(shell ls all/alancoding-everything-*.tar.gz | tail -1)

build:
	rm -rf alancoding-deps-*.tar.gz
	ansible-galaxy collection build -vvv

just_install:
	ANSIBLE_COLLECTIONS_PATHS=target ansible-galaxy collection install $(BUNDLE) -f -p target -vvv

install:
	rm -rf target
	make just_install

install_one:
	rm -rf target/ansible_collections/alancoding/deps/
	make just_install

build_all:
	rm -rf all/alancoding-everything-*.tar.gz
	ansible-galaxy collection build all --output-path=all -vvv

just_install_all:
	ANSIBLE_COLLECTIONS_PATHS=all/target ansible-galaxy collection install $(ALL_BUNDLE) -p all/target -vvv

install_all:
	rm -rf all/target
	make just_install_all