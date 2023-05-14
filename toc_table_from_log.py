#!/usr/bin/env python

import re
import sqlite3
import sys
import json


### Parameters
ARTICLE_TABLE = 'articles'
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

# Create the "toc" table, if it doesn't exist, with rows called "id", "title", "refs".
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TOC_TABLE}(
        id INTEGER PRIMARY KEY,
        term TEXT NOT NULL,
        refs TEXT)
''')

# Read dict from the standard input, one line at a time.
# TODO: Eventually this will be a log file.
n = 0
for line in sys.stdin:
    # Print a status message to stderr every 100 lines read.
    n += 1
    if n % 100 == 0:
        print("Read %d lines" % n, file=sys.stderr)

    # Remove leading and trailing whitespace.
    line = line.strip()

    # Query the first database for rows where the 'title' column starts with the
    # line just read. Use the SQLite LIKE operator for a case-insensitive match.
    # TODO: Take this list of titles (or title) from the log file.
    cursor.execute(f"SELECT * FROM {ARTICLE_TABLE} WHERE title LIKE ?;", (line+'%',))

    # Create a list of all the validated titles from the rows returned.
    titles = [row[1] for row in cursor.fetchall()]
    
    # Print "line: titles" to stderr.
    print("%s: %s" % (line, titles), file=sys.stderr) 

    # Add a row to the "toc" table with the line just read as the "term" column.
    # The "references" column should be a JSON-encoded list of the titles found.
    cursor.execute(f"INSERT INTO {TOC_TABLE} (term, refs) VALUES (?, ?);",
                     (line, json.dumps(titles)))
    
    # Now, go through each title in titles and find the corresponding row in the "articles" table.
    # Add the title to the "references" column of that row.
    for title in titles:
        cursor.execute(f"SELECT * FROM {ARTICLE_TABLE} WHERE title = ?;", (title,))
        row = cursor.fetchone()
        if row is None:
            print("Error: Could not find row for title '%s'" % title, file=sys.stderr)
        else:
            # Check to see if row[4] is None. If it is, set refs_in to an empty list.
            if row[4] is "":
                refs_in = []
            else:
                # Decode the JSON-encoded list of references.
                refs_in = json.loads(row[4])
            # Add the line just read to the list of references.
            refs_in.append(line)
            # Remove duplicates from the list of references.
            refs_in = list(set(refs_in))
            # Update the row with the new list of references.
            cursor.execute(f"UPDATE {ARTICLE_TABLE} SET see_also = ? WHERE title = ?",
                           (json.dumps(refs_in), title))

# Close the connections to both databases.
conn.close()
