#!/bin/bash

# Generate XHTML encyclopedia
# TODO: Should eventually be a Makefile

mkdir ./html
cp -f styles.css html
python extract_dict.py 
python extract_indices.py
python extract_toc.py
