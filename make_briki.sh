#!/bin/bash

# Generate briki.html
# TODO: Should eventually be a Makefile

rm -f briki_test.html
python extract_dict.py < dict > briki.html
