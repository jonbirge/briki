#!/usr/bin/env python

# Filter out lines that contain non-ASCII characters or short words

import sys

def filter_lines(lines_in):
    lines_out = []
    for line in lines_in:
        if len(line) > 3 and not contains_non_ascii(line):
            lines_out.append(line)
    return lines_out

def contains_non_ascii(s):
    return any(ord(c) > 127 for c in s)

if __name__ == "__main__":
    lines_in = sys.stdin.readlines()
    lines_out = filter_lines(lines_in)
    lines_out.sort()
    sys.stdout.writelines(lines_out)
