#!/usr/bin/env python

import sys
import sqlite3

# get database from command line
if len(sys.argv) < 2:
    database = "briki.db"
else:
    database = sys.argv[1]

# open briki.db for reading
print("Opening %s for reading..." % database)
conn = sqlite3.connect(database)
cursor = conn.cursor()

# print the name and the number of rows in each table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for table in cursor.fetchall():
    cursor.execute("SELECT COUNT(*) FROM %s;" % table)
    print("%s: %s" % (table[0], cursor.fetchone()[0]))
