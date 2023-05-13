#!/usr/bin/env python

import os
import sys
import re
import time
import sqlite3


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
for row in cursor:
    title = row[0]
    contents = row[1]
    print("*%s*: %s" % (title, contents))

# TODO Clean up the contents using clean_contents function
    
# Close the connection
conn.close()
