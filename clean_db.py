#!/usr/bin/env python

import os
import sys
import re
import time
import sqlite3


# GPT-4 instructions:
# Function to take a string and return a cleaned up version.
# Remove all cases of poor formatting, such as:
# - Multiple spaces
# - Multiple newlines
# - Leading and trailing spaces
# - Leading and trailing newlines
# - Extra spaces before and after punctuation
# Here is the function:
def clean_contents(contents):
    # Remove multiple spaces
    contents = re.sub(" +", " ", contents)
    # Remove multiple newlines
    contents = re.sub("\n+", "\n", contents)
    # Remove leading and trailing spaces
    contents = contents.strip()
    # Remove leading and trailing newlines
    contents = contents.strip("\n")
    # Remove extra spaces before and after punctuation
    contents = re.sub(" +([.,;:?!])", r"\1", contents)
    contents = re.sub("([.,;:?!]) +", r"\1", contents)
    return contents

# Command line handling
if len(sys.argv) < 2:
    filename = "briki.db"
else:
    filename = sys.argv[1]

# Backup the database
backup_filename = filename + "." + time.strftime("%Y%m%d%H%M%S")
print("Backing up %s to %s..." % (filename, backup_filename))
os.system("cp %s %s" % (filename, backup_filename))

# Connect to SQLite database
conn = sqlite3.connect(filename)
cursor = conn.cursor()

# Get the title and contents of each row from the articles table
cursor.execute('''
    SELECT title, contents
    FROM articles
    ORDER BY title
''')

# Print the title and contents of each row in the format *title*: contents
n = 0
for row in cursor:
    n += 1
    if n % 1000 == 0:
        print("Processed %d entries" % n, file=sys.stderr)

    # Extract relevent data from row
    id = row[0]
    title = row[1]
    contents = row[2]

    # Clean up the contents
    contents = clean_contents(contents)

    # Update the row in the database
    cursor.execute('''
        UPDATE articles
        SET contents = ?
        WHERE id = ?
    ''', (contents, id))

# Commit the changes
conn.commit()

# Close the connection
conn.close()
