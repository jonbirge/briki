#!/usr/bin/env python

import sys
import re
import time
import sqlite3
import datetime
import wikipediaapi


### Parameters
DEFAULT_PAGES = ["Wikipedia:Vital articles/Level/5"]
DEFAULT_DEPTH = 2
THROTTLE_TIME = 0.5
FILENAME = "wiki_titles"


### Functions

def remove_extra_spaces(text):
    # Use a regular expression to add a space after every period that's
    # followed by a non-space character or a non-digit character
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

def is_good_link(title):
    # Check if the title is a good title for our purposes
    return title.startswith("Wikipedia:Vital articles/Level/")

def is_good_final_title(title):
    return (len(title) > 2 and
                not "(disambiguation)" in title and
                not title.startswith("Talk:") and
                not title.startswith("Help:") and
                not title.startswith("Category:") and
                not title.startswith("Template:") and
                not title.startswith("User:") and
                not title.startswith("Wikipedia:Contents") and
                not title.startswith("Wikipedia talk:") and
                not title.startswith("Template talk:") and
                not title.startswith("User talk:") and
                not title.startswith("Portal:") and
                not title.startswith("File:") and
                not title.startswith("Module:"))

def filter_links(links):
    # Filter out titles that are not good links to follow
    links_filtered = []
    for link in links:
        if is_good_link(link):
            links_filtered.append(link)
    return links_filtered

def filter_titles(titles):
    # Filter out titles that are not good articles to keep
    titles_filtered = []
    for title in titles:
        if is_good_final_title(title):
            titles_filtered.append(title)
    return titles_filtered

# Function to take a page and return a list of all the valid wikipedia articles linked from that page.
def get_linked_titles(wiki_page):
    # Check raw_title and return a (potentially empty) list of validated titles
    link_titles = []
    try:
        if wiki_page.exists():
            for link in wiki_page.links:
                link_titles.append(link)
        else:
            print("*** Warning: %s does not exist." % wiki_page.title, file=sys.stderr)
    except Exception as e:
        print("*** Error pulling links from %s: %s" % (wiki_page, e), file=sys.stderr)
        link_titles = []
    return link_titles

def recurse_page(page, max_depth, depth=0):
    # Recursively get all the linked titles from a page
    # Return a list of all the titles
    print("Recursing page %s at depth %d..." % (page.title, depth), file=sys.stderr)
    linked_titles = get_linked_titles(page)
    depth += 1
    if depth < max_depth:
        output_links = []
        follow_links = filter_links(linked_titles)
        for linked_title in follow_links:
            time.sleep(THROTTLE_TIME)
            linked_page = wiki.page(linked_title)
            output_links.extend(recurse_page(linked_page, max_depth, depth))
        return output_links
    else:
        return filter_titles(linked_titles)            
    

### Main

# Get all links from the priority categories
wiki = wikipediaapi.Wikipedia('en')
main_article_titles = []

for start_article in DEFAULT_PAGES:
    time.sleep(THROTTLE_TIME)
    start_page = wiki.page(start_article)
    main_article_titles.extend(recurse_page(start_page, DEFAULT_DEPTH))

# Sort and remove duplicates
main_article_titles = sorted(list(set(main_article_titles)))

# Open output file and write titles
output_file = open(FILENAME, 'w')
for title in main_article_titles:
    output_file.write(title + "\n")

# Close output file
output_file.close()
