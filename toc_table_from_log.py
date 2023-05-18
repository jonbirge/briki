#!/usr/bin/env python

import re
import sqlite3
import sys
import json
import ast


### Parameters
ARTICLES_TABLE = 'articles'
TOC_TABLE = 'contents'

### Functions


### Main

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = "briki.db"
else:
    db_name = sys.argv[1]

# Connect to the database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Drop the "contents" table, if it exists.
# ...

# Create the "contents" table, if it doesn't exist, with rows called "id", "title", "refs".
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TOC_TABLE}(
        id INTEGER PRIMARY KEY,
        term TEXT NOT NULL,
        refs TEXT NOT NULL)
''')

# Read log from the standard input, one line at a time.
read_next = False
n = 0
for log_line in sys.stdin:
    n += 1
    if n % 100 == 0:
        print(f"Read {n} lines...", file=sys.stderr)

    # Remove leading and trailing whitespace.
    log_line = log_line.strip()

    # Check to see if line is of the form "X links to Y, a disambiguation page."
    if not read_next:
        match = re.match(r'^(.+) links to (.*)\.$', log_line)
        if match:
            term = match.group(1)
            something = match.group(2)
            print(f"{term} links to {something}, will get next line...")
            read_next = True
        titles = []
    else:
        read_next = False
        # Check to see if line is of form "Valid Titles: X"
        match = re.match(r'^Valid titles: (.*)$', log_line)
        if match and term != "":
            titles_str = match.group(1)
            titles = ast.literal_eval(titles_str)
            print(f"{term} points to {titles}.")
        else:
            titles = []
            term = ""

    # Add reference(s) to database...
    if len(titles) > 0:
        print(f"Adding {term} row to toc table...")
        refs = []
        for title in titles:
            cursor.execute(f"SELECT id FROM {ARTICLES_TABLE} WHERE title = ?;", (title,))
            id = cursor.fetchone()[0]
            refs.append(id)
        
        refs_json = json.dumps(refs)
        print(f"Found refs: {refs_json}")
        cursor.execute(f"INSERT INTO {TOC_TABLE} (term, refs) VALUES (?, ?);",
                        (term, refs_json))

        # Now, go through each title in titles and find the corresponding row in the "articles" table.
        # Add the title to the "references" column of that row.
        # for title in titles:
        #     cursor.execute(f"SELECT * FROM {ARTICLE_TABLE} WHERE title = ?;", (title,))
        #     row = cursor.fetchone()
        #     if row is None:
        #         print("Error: Could not find row for title '%s'" % title)
        #     else:
        #         # Check to see if row[4] is None. If it is, set refs_in to an empty list.
        #         if row[4] == "":
        #             refs_in = []
        #         else:
        #             # Decode the JSON-encoded list of references.
        #             refs_in = json.loads(row[4])
        #         # Add the line just read to the list of references.
        #         refs_in.append(term)
        #         # Remove duplicates from the list of references.
        #         refs_in = list(set(refs_in))
        #         # Update the row with the new list of references.
        #         cursor.execute(f"UPDATE {ARTICLE_TABLE} SET see_also = ? WHERE title = ?",
        #                     (json.dumps(refs_in), title))

# Commit the changes to the database.
conn.commit()

# Close the connections to both databases.
conn.close()
