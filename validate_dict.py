#!/usr/bin/env python

import sys
import re
import wikipediaapi
import sqlite3


### Output list of validated titles to a file...

def is_good_title(title):
    # Check if the title is a good title
    return (len(title) > 2 and 
            not title.startswith("Talk:") and
            not title.startswith("Help:"))

def filter_titles(titles):
    # Filter out titles that are not good titles
    titles_filtered = []
    for line in titles:
        if is_good_title(line):
            titles_filtered.append(line)
    return titles_filtered

def validated_titles(raw_title, wiki):
    # Check raw_title and return a (potentially empty) list of validated titles
    # TODO: check for foreign characters or short names
    titles = []
    page = wiki.page(raw_title)
    if page.exists():
        if "Category:All disambiguation pages" in page.categories:
            print("%s is a disambiguation page." % page.title)
            for link in page.links:
                titles.append(link)
                print("Link: %s" % link)
        else:
            print("%s is a valid page." % page.title)
            titles.append(page.title)

    # Check for 
    return filter_titles(titles)

# Read in the file of article titles from stdin, or a default file name if there is not stdin
if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = 'dict_test'

# Open the file and read in the lines into a string array
with open(file_name) as f:
    dict_raw = f.readlines()

# Print the number of elements in dict_raw
print("Number of elements in dict_raw: %d" % len(dict_raw))

### Validate each entry in dict_raw
wiki = wikipediaapi.Wikipedia('en')
valid_set = set()
for entry in dict_raw:
    # Remove the newline character from the end of the entry
    entry = entry.rstrip('\n')

    # Check to see if the entry is a valid article title
    # If it is, add it to the dict_valid array
    print("Checking: %s" % entry)
    new_entries = validated_titles(entry, wiki)
    if len(new_entries) > 0:
        valid_set.update(set(new_entries))

# Create a sorted list from the set
dict_valid = list(valid_set)
dict_valid.sort()

# Print the number of elements in dict_valid
print("Number of elements in dict_valid: %d" % len(dict_valid))

# Write the validated titles to a file
with open('dict_valid', 'w') as f:
    for entry in dict_valid:
        f.write("%s\n" % entry)
