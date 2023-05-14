#!/usr/bin/env python

import re
import sqlite3
import sys


### Create a new database with words related to those provided in the standard input.

# Function that takes a string and returns the string with all repeated white
# spaces replaces with a single space.
def remove_extra_spaces(string):
    return re.sub(r'\s+', ' ', string)

# Check if the correct number of arguments have been provided.
if len(sys.argv) != 2:
    print('Usage: python script.py <database>')
    sys.exit(1)

# The first and second command line arguments are the names of the databases.
db_name = sys.argv[1]

# Connect to the first database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Fetch the name of the first table in the first database.
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_name = cursor.fetchone()[0]

# Read from the standard input, one line at a time.
n = 0
for line in sys.stdin:
    # Print a status message to stderr every 100 lines read.
    n += 1
    if n % 100 == 0:
        print("Read %d lines" % n, file=sys.stderr)

    # Remove leading and trailing whitespace.
    line = line.strip()

    # Query the first database for rows where the 'title' column starts with the line just read.
    # Use the SQLite LIKE operator for a case-insensitive match.
    cursor.execute(f"SELECT * FROM {table_name} WHERE title LIKE ?;", (line+'%',))

    # Fetch all the matching rows.
    rows = cursor.fetchall()

    # For each matching row...
    for row in cursor:
        title = row[0]
        contents = remove_extra_spaces(row[1])
        print("*%s*: %s" % (title, contents))
        print("")

# Close the connections to both databases.
conn.close()
