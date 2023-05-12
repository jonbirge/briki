#!/usr/bin/env python

import sys
import re
import sqlite3
import datetime
import wikipediaapi


### Parameters
# BATCH_SIZE = 128  # number of articles to process at a time (eventually)

def clean_summary(text):
    # Use a regular expression to add a space after every period that's
    # followed by a non-space character or a non-digit character
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

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

def validated_titles(raw_title):
    # Check raw_title and return a (potentially empty) list of validated titles
    # TODO: check for foreign characters or short names
    titles = []
    try:
        page = wiki.page(raw_title)
        if page.exists():
            if "Category:All disambiguation pages" in page.categories:
                print("%s links to %s, a disambiguation page." % (raw_title, page.title))
                for link in page.links:
                    titles.append(link)
                titles = filter_titles(titles)
            else:
                print("%s links to %s." % (raw_title, page.title))
                titles.append(page.title)
    except Exception as e:
        print("*** Error validating %s: %s" % (raw_title, e))
        titles = []
    return titles

def pull_valid_article(title):
    # Add a valid article to the articles table from the Wikipedia API

    # Check to see if the title is already in the articles table
    # TODO: Also check date_update to see if it is out of date
    cursor.execute('SELECT * FROM articles WHERE title=?', (title,))
    row = cursor.fetchone()
    if row is None:  # We don't have this one yet.
        print("Pulling %s into to database..." % title)
        try:
            page = wiki.page(title)
            contents = clean_summary(page.summary)

            # Get the current data and time
            date_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert the title, date_update, contents, see_also, and see_from into the articles table
            cursor.execute('''
                INSERT INTO articles(title, date_update, contents, see_also)
                VALUES(?, ?, ?, ?)''', (title, date_update, contents, see_also))
            conn.commit()
        except Exception as e:
            print("*** Error pulling %s: %s" % (title, e))
    else:
        print("Skipping %s since it's already in the database." % title)

def add_title(title):
    # Add a title to the articles table from the Wikipedia API, first checking
    # to see if it's valid or leads to disambiguation

    print("Checking new title %s..." % title)
    # If the title is not in the articles table, check to see if it's a valid title
    valid_title_list = filter_titles(validated_titles(title))
    print("Valid titles: %s" % valid_title_list)
    
    # Check to see if it's a valid article or redirected
    if len(valid_title_list) > 0:
        if len(valid_title_list) == 1:
            # If it's a valid article, pull it from Wikipedia
            pull_valid_article(valid_title_list[0])
        else:
            # Run add_title on each title in valid_titles
            for valid_title in valid_title_list:
                pull_valid_article(valid_title)


### Create SQLite database and tables, if needed...

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('bliki.db')
cursor = conn.cursor()

# Check to see if articles table exists and if it doesn't create it...
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        date_update TEXT,
        contents TEXT,
        see_also TEXT)
''')
               

### Update the database of definitions for dict_test...

# Read each line of dict_test into an array
with open('dict_test') as f:
    dict = f.readlines()

# Run through all titles and pull the contents from Wikipedia
# TODO: Thread this
wiki = wikipediaapi.Wikipedia('en')
for raw_title in dict:
    # Remove the newline character from the end of the title
    raw_title = raw_title.rstrip('\n')

    # Add the title to the articles table
    add_title(raw_title)
        
# Close the database
conn.close()
