#!/usr/bin/env python

# Removes extraneous information from the database, writing a new database.

import re
import sqlite3
import sys
import os
import json


### Parameters
ARTICLES_TABLE = 'articles'
TOC_TABLE = 'contents'
NEW_DB_NAME = 'briki_abridged.db'


### Functions

def process_toc_row(toc_row):
    # Get the word and extract the JSON-encoded list of refs.
    id = toc_row[0]
    title = toc_row[1]
    ref_ids = json.loads(toc_row[2])

    # Get the titles of all articles in the list of refs.
    keep_ids = []
    for ref_id in ref_ids:
        cursor_orig.execute(f"SELECT title FROM {ARTICLES_TABLE} WHERE id = {ref_id};")
        article_title = cursor_orig.fetchone()[0]
        # If title is the beginning of article_title, keep it. Ignore capitalization.
        if title.lower() in article_title.lower():
            # Keep the reference.
            keep_ids.append(ref_id)
            # Copy the article to the new database if it doesn't already exist.
            cursor_new.execute(f"SELECT * FROM {ARTICLES_TABLE} WHERE id = {ref_id};")
            if cursor_new.fetchone() is None:
                # n_kept += 1
                cursor_orig.execute(f"SELECT * FROM {ARTICLES_TABLE} WHERE id = {ref_id};")
                art = cursor_orig.fetchone()
                cursor_new.execute(f"INSERT INTO {ARTICLES_TABLE} (id, title, date_update, contents, see_also) \
                                   VALUES (?, ?, ?, ?, ?);", (ref_id, art[1], art[2], art[3], art[4]))
    
    # Write new TOC entry.
    new_refs_json = json.dumps(keep_ids)
    cursor_new.execute(f"INSERT INTO {TOC_TABLE} (id, title, refs) VALUES (?, ?, ?);", \
                        (id, title, new_refs_json))
    
    # Commit changes to the new database.
    conn_new.commit()
    

### Main

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = "briki.db"
else:
    db_name = sys.argv[1]

# Connect to the original database.
conn_orig = sqlite3.connect(db_name)
cursor_orig = conn_orig.cursor()

# Create a new database and connect to it.
conn_new = sqlite3.connect(NEW_DB_NAME)
cursor_new = conn_new.cursor()

# Delete the old tables.
cursor_new.execute(f"DROP TABLE IF EXISTS {ARTICLES_TABLE};")
cursor_new.execute(f"DROP TABLE IF EXISTS {TOC_TABLE};")

# Create the new tables.
cursor_new.execute(f"CREATE TABLE {ARTICLES_TABLE} \
                   (id INTEGER PRIMARY KEY, title TEXT, date_update TEXT, contents TEXT, see_also TEXT);")
cursor_new.execute(f"CREATE TABLE {TOC_TABLE} (id INTEGER PRIMARY KEY, title TEXT, refs TEXT);")
conn_new.commit()

# Read every row from the "contents" table.
# Each row is a tuple of (word, refs).
# Refs is a list of article IDs in JSON format.
cursor_orig.execute(f"SELECT * FROM {TOC_TABLE};")
toc_list = cursor_orig.fetchall()

# Loop through all entries in the original TOC.
n = 0
# n_kept = 0
for toc_row in toc_list:
    n += 1
    if n % 250 == 0:
        print("Processed %d toc entries" % n, file=sys.stderr)
    process_toc_row(toc_row)

# Print the number of articles kept.
# print("Kept %d articles" % n_kept, file=sys.stderr)

# Close the databases.
conn_orig.close()
conn_new.close()
