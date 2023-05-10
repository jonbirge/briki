#!/usr/bin/env python

import sys

def filter_ascii_lines():
    for line in sys.stdin:
        if len(line) >= 3 and not contains_non_ascii(line):
            sys.stdout.write(line)

def contains_non_ascii(s):
    return any(ord(c) > 127 for c in s)

if __name__ == "__main__":
    filter_ascii_lines()
