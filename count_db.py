#!/usr/bin/env python

import sqlite3

# open briki.db for reading
conn = sqlite3.connect('briki.db')
cursor = conn.cursor()

# print the name and the number of rows in each table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for table in cursor.fetchall():
    cursor.execute("SELECT COUNT(*) FROM %s;" % table)
    print("%s: %s" % (table[0], cursor.fetchone()[0]))
