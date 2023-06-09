#!/usr/bin/env python

import sqlite3
import sys


# If a command line argument is provided, use it as the database file name
# Otherwise, use 'default.db' as the default name
db_file = sys.argv[1] if len(sys.argv) > 1 else 'briki.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)

# Create a cursor object
c = conn.cursor()

# Get the first 10 rows from the table
c.execute(f"SELECT * FROM articles LIMIT 10;")

# Fetch all the rows
rows = c.fetchall()

# Print the rows
for row in rows:
    print(row)
    print("---")

# Close the connection
conn.close()
