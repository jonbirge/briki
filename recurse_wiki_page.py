#!/usr/bin/env python

import sys
import re
import time
import sqlite3
import datetime
import wikipediaapi


### Parameters
DEFAULT_DB = "briki_test.db"
#DEFAULT_PAGE = "Swarthmore_College"
DEFAULT_PAGE = "Wikipedia:Vital articles/Level/5"
THROTTLE_TIME = 0.5


### Functions

def remove_extra_spaces(text):
    # Use a regular expression to add a space after every period that's
    # followed by a non-space character or a non-digit character
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

def is_good_link(title):
    # Check if the title is a good title
    if title.startswith("Wikipedia:Vital"):
        return True
    else:
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
                not title.startswith("Module:"))

def is_good_final_title(title):
    return (is_good_link(title) and
            not title.startswith("Wikipedia:"))

def filter_links(links):
    # Filter out link titles that are not good to follow
    links_filtered = []
    for link in links:
        if is_good_link(link):
            links_filtered.append(link)
    return links_filtered

def filter_titles(titles):
    # Filter out titles that are not good titles
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
                print("Found link %s" % link, file=sys.stderr)
                link_titles.append(link)
        else:
            print("*** Warning: %s does not exist." % wiki_page.title, file=sys.stderr)
    except Exception as e:
        print("*** Error pulling links from %s: %s" % (wiki_page, e), file=sys.stderr)
        link_titles = []
    return filter_links(link_titles)

def recurse_page(page, max_depth, depth=0):
    # Recursively get all the linked titles from a page
    # Return a list of all the titles
    print("Recursing page %s..." % page.title, file=sys.stderr)
    linked_titles = get_linked_titles(page)
    depth += 1
    if depth < max_depth:
        for linked_title in linked_titles:
            time.sleep(THROTTLE_TIME)
            linked_page = wiki.page(linked_title)
            linked_titles.extend(recurse_page(linked_page, max_depth, depth))
    return linked_titles
    

### Main

# Command line handling          
if len(sys.argv) < 2:
    start_article = DEFAULT_PAGE
else:
    filename = sys.argv[1]

# Get all links from the main article
wiki = wikipediaapi.Wikipedia('en')
start_article = wiki.page(DEFAULT_PAGE)
main_article_titles = recurse_page(start_article, 2)

# Write all linked article titles to stdout
for title in main_article_titles:
    print(title)
