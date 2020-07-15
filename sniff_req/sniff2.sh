#!/bin/sh


# time grep -r "DOCUMENTATION" target/ansible_collections/arista/eos --include \*.py | python sniff_req/sniff2.py

time grep -r "DOCUMENTATION" target/ --include \*.py | python sniff_req/sniff2.py

