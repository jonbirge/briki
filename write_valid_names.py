#!/usr/bin/env python

import sys
import wikipediaapi
import re

def add_space_after_period(text):
    # Use a regular expression to add a space after every period that's
    # followed by a non-space character
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

wiki = wikipediaapi.Wikipedia('en')

page = wiki.page('Python')

# Check to see if page is a disambiguation page.
# If it is create a string array called page_links with all the referenced articles.
if page.exists():
    if "Category:All disambiguation pages" in page.categories:
        print("%s is a disambiguation page." % page.title)
        summary = "Disambiguation page."
        page_links = []
        for link in page.links:
            page_links.append(link)
            print("Link: %s" % link)
    else:
        summary = add_space_after_period(page.summary)
else:
    summary = "Page does not exist."

print("Summary: \n%s\n" % summary)
