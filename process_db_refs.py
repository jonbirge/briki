#!/usr/bin/env python

import json
import sqlite3
import sys
import time
import os
import re


### Parameters
ARTICLE_TABLE = "articles"
DB_FILE = "briki.db"


### Open database

# Connect to the database.
conn = sqlite3.connect(DB_FILE)
main_cursor = conn.cursor()
cursor = conn.cursor()

# Read rows from the "articles" table.
main_cursor.execute(f"SELECT * FROM {ARTICLE_TABLE};")

# Read the database one row at a time.
n = 0
row = main_cursor.fetchone()
while row is not None:
    n += 1
    if n % 100 == 0:
        print("Processed %d articles" % n, file=sys.stderr)

    # Process the row and update index.
    id = row[0]
    links = json.loads(row[4])
    new_links = []
    for link in links:
        # check to see if link is a tuple
        if isinstance(link, tuple):
            new_links.append(link)  # already done
        else:
            title = link
            # search for title in database and retrieve id
            cursor.execute(f"SELECT id FROM {ARTICLE_TABLE} WHERE title = ?;", (title,))
            link_row = cursor.fetchone()
            if link_row is not None:
                link_id = link_row[0]
                new_links.append((title, link_id))

    # update database
    new_links = json.dumps(new_links)
    cursor.execute(f"UPDATE {ARTICLE_TABLE} SET see_also = ? WHERE id = ?;", (new_links, id))
    conn.commit()

    # Fetch the next row
    row = main_cursor.fetchone()

# Close the database.
conn.close()
