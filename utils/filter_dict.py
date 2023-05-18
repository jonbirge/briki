#!/usr/bin/env python

# Filter out lines that contain non-ASCII characters or short words

import sys

# Return True if the line is good, False otherwise.
def is_good_line(the_line):
    return (len(the_line) > 3 and
            not contains_non_ascii(the_line) and
            not the_line.endswith("'s"))

# Return True if the string contains non-ASCII characters, False otherwise.
def contains_non_ascii(s):
    return any(ord(c) > 127 for c in s)

# Search through list of lines and remove lines that are just the plural of
# another line somewhere else in the list. This function operates on the list in
# place.
def remove_plurals(lines):
    def is_plural(s):
        return s.endswith('s') and s[:-1] in lines
    i = 0
    while i < len(lines):
        if is_plural(lines[i]):
            del lines[i]
        else:
            i += 1

# Function that takes a list of lines, and removes those lines which are not
# good according to is_good_line. This function operates on the list in place.
def filter_lines(lines):
    i = 0
    while i < len(lines):
        if not is_good_line(lines[i]):
            del lines[i]
        else:
            i += 1

# Read all the lines from standard input, stripping newlines from the end of each.
lines = [line.strip() for line in sys.stdin]  # List comprehension

# Sort the lines, filter out the bad ones, and remove plurals.
lines.sort()
filter_lines(lines)
remove_plurals(lines)

# Write the lines to standard output, adding newlines back in.
for line in lines:
    print(line)
