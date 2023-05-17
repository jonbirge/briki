#!/bin/bash

# Generate briki.html
# TODO: Should eventually be a Makefile

python extract_dict.py 
#python extract_toc.py
cp -f styles.css html
