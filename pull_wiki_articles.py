#!/usr/bin/env python

import sys
import re
import time
import json
import sqlite3
import datetime
import wikipediaapi


### Parameters
THROTTLE_TIME = 0.5
DEFAULT_ARTICLE_LIST = 'level_4_titles.txt'  # default to short list of titles
DB_FILE = 'briki.db'
ARTICLE_TABLE = 'articles'


# Functions

# Use a regular expression to add a space after every period that's
# followed by a non-space character or a non-digit character
def clean_summary(text):
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

# Remove extra white space in string.
def remove_extra_spaces(string):
    return re.sub(r"\s+", " ", string)

# Take a string with newline characters and return a list of paragraphs.
def split_into_paragraphs(string):
    return string.split("\n")

def pull_article(title):
    # Check to see if the title is already in the articles table
    # TODO: Also check date_update to see if it is out of date
    cursor.execute('SELECT * FROM articles WHERE title=?', (title,))
    row = cursor.fetchone()

    if row is None:  # We don't have this one yet.
        print("Pulling %s into to database..." % title)
        try:
            # grab page from Wikipedia
            time.sleep(THROTTLE_TIME)
            page = wiki.page(title)
            contents = clean_summary(page.summary)

            # Get the current data and time
            date_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get links to other pages in the 'See also' section, if it exists
            sections = page.sections
            see_also_text = ''
            for s in sections:
                if s.title == 'See also':
                    see_also_text = s.text
                    break
            see_also = split_into_paragraphs(see_also_text)
            see_also_json = json.dumps(see_also)

            # Insert the title, date_update, contents, see_also, and see_from into the articles table
            cursor.execute('''
                INSERT INTO articles(title, date_update, contents, see_also)
                VALUES(?, ?, ?, ?)''', (title, date_update, contents, see_also_json))
            conn.commit()
        except Exception as e:
            print("*** Error pulling %s: %s" % (title, e))
    else:
        print("Skipping %s since it's already in the database." % title)


### Main

# Command line handling          
if len(sys.argv) < 2:
    filename = DEFAULT_ARTICLE_LIST
else:
    filename = sys.argv[1]

# Connect to SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Check to see if articles table exists and if it doesn't create it...
# TODO: Rename see_also to refs_in
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        date_update TEXT,
        contents TEXT,
        see_also TEXT)
''')
  
# Read each line of dict_test into an array
with open(filename) as f:
    dict = f.readlines()

# Run through all titles and pull the contents from Wikipedia
wiki = wikipediaapi.Wikipedia('en')
for the_title in dict:
    # Remove the newline character from the end of the title
    the_title = the_title.rstrip('\n')

    # Add the title to the articles table
    pull_article(the_title)
        
# Close the database
conn.close()
