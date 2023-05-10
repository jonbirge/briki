#!/usr/bin/env python

import sys
import re
import wikipediaapi
import sqlite3

def add_space_after_period(text):
    # Use a regular expression to add a space after every period that's
    # followed by a non-space character or a non-digit character
    return re.sub(r'\.(?=[^\s\d])', '. ', text)

### Create SQLite database and tables, if needed...

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('bliki.db')

# Create a cursor object
cursor = conn.cursor()

# Check to see if articles table exists and if it doesn't create it...
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        date_update TEXT,
        contents TEXT,
        see_also TEXT,
        see_from TEXT)
''')
               
# Read each line of dict_test
with open('dict_test') as f:
    dict_titles = f.readlines()

# Write each element of dict_titles to the articles table if it doesn't already exist
for title in dict_titles:
    # Remove the newline character from the end of the title
    title = title.rstrip('\n')

    # Check to see if the title is already in the articles table
    cursor.execute('SELECT * FROM articles WHERE title=?', (title,))
    row = cursor.fetchone()
    if row is None:
        # If the title is not in the articles table, add it
        print("Adding %s to articles table" % title)
        cursor.execute('INSERT INTO articles(title) VALUES(?)', (title,))
    else:
        print("%s is already in the articles table" % title)

# Commit changes to the database
conn.commit()

# Close the database connection
conn.close()
