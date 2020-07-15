#!/bin/sh

time grep -r "DOCUMENTATION" target/ --include \*.py | python sniff_req/sniff2.py

