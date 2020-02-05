VERSION=1.0.1

build:
	rm -rf alancoding-deps-$(VERSION).tar.gz
	ansible-galaxy collection build

just_install:
	ANSIBLE_COLLECTIONS_PATHS=target ansible-galaxy collection install alancoding-deps-$(VERSION).tar.gz -p target

install:
	rm -rf target
	make just_install

install_one:
	rm -rf target/ansible_collections/alancoding/deps/
	make just_install

