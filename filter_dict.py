#!/usr/bin/env python

# Filter out lines that contain non-ASCII characters or short words

import sys

def is_good_line(the_line):
    the_line = the_line.strip()
    return (len(the_line) > 3 and
            not contains_non_ascii(the_line) and
            not the_line.endswith("'s"))

def contains_non_ascii(s):
    return any(ord(c) > 127 for c in s)

def old_filter_lines(lines):
    new_lines = []
    for line in lines:
        if is_good_line(line):
            new_lines.append(line)
    return new_lines

def filter_lines(lines):
    return [line for line in lines if is_good_line(line)]

if __name__ == "__main__":
    lines_in = sys.stdin.readlines()
    lines_out = filter_lines(lines_in)
    lines_out.sort()
    sys.stdout.writelines(lines_out)
