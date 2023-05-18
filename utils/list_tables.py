#!/usr/bin/env python

import sqlite3
import sys


# If a command line argument is provided, use it as the database file name
# Otherwise, use 'default.db' as the default name
db_file = sys.argv[1] if len(sys.argv) > 1 else 'briki.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)

# Create a cursor object
cursor = conn.cursor()

# Execute the query that retrieves all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch all results of the query
tables = cursor.fetchall()

# Close the connection
conn.close()

# Extract table names and print them
for table in tables:
    print(table[0])
