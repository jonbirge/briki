#!/usr/bin/env python

import sqlite3
import sys
import csv

def main():
    # Check if the correct number of arguments have been provided.
    if len(sys.argv) != 3:
        print('Usage: python script.py <database1> <database2>')
        sys.exit(1)

    # The first and second command line arguments are the names of the databases.
    db1_name = sys.argv[1]
    db2_name = sys.argv[2]

    # Connect to the first database.
    conn1 = sqlite3.connect(db1_name)
    cursor1 = conn1.cursor()

    # Connect to the second database.
    conn2 = sqlite3.connect(db2_name)
    cursor2 = conn2.cursor()

    # Fetch the name of the first table in the first database.
    cursor1.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_name = cursor1.fetchone()[0]

    # Read from the standard input, one line at a time.
    for line in sys.stdin:
        line = line.strip()

        # Query the first database for rows where the 'title' column starts with the line just read.
        # Use the SQLite LIKE operator for a case-insensitive match.
        cursor1.execute(f"SELECT * FROM {table_name} WHERE title LIKE ?;", (line+'%',))

        # Fetch all the matching rows.
        rows = cursor1.fetchall()

        # For each matching row...
        for row in rows:
            # Prepare the placeholders for the INSERT statement.
            placeholders = ', '.join('?' * len(row))
            # Insert the row into the second database.
            cursor2.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

    # Commit the changes to the second database.
    conn2.commit()

    # Close the connections to both databases.
    conn1.close()
    conn2.close()

if __name__ == "__main__":
    main()
