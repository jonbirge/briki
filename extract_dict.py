#!/usr/bin/env python

import re
import sqlite3
import sys


### Parameters
TABLE_NAME = 'articles'


### Functions

def begin_html_document():
    sys.stdout.write('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Brikipaedia</title>
<! <link rel="stylesheet" href="styles.css"> /!>
</head>

<body>
    ''')

def add_article(title, content, from_dict):
    sys.stdout.write(f'''
<article>
<h1>{title}</h1>
    ''')
    add_content_paragraphs(content)
    add_content_paragraphs([f"(From {from_dict})"])

    sys.stdout.write('''
</article>
    ''')

def add_content_paragraphs(paragraphs):
    for paragraph in paragraphs:
        sys.stdout.write(f'<p>{paragraph}</p>\n')

def end_html_document():
    sys.stdout.write('''
<footer>
<p>© 2023 Jonathan Birge. All rights reserved.</p>
</footer>
</body>
</html>
    ''')

# Example usage
# add_article('Leonardo da Vinci', [
#     'Leonardo da Vinci was an Italian polymath...',
#     'He showed remarkable artistic talent...'
# ])

# Function that takes a string and returns the string with all repeated white
# spaces replaced with a single space.
def remove_extra_spaces(string):
    return re.sub(r'\s+', ' ', string)


### Main

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = "briki.db"
else:
    db_name = sys.argv[1]

# Connect to the first database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Read from the standard input, one line at a time.
n = 0
begin_html_document()
for line in sys.stdin:
    # Print a status message to stderr every 100 lines read.
    n += 1
    if n % 100 == 0:
        print("Read %d lines" % n, file=sys.stderr)

    # Remove leading and trailing whitespace.
    line = line.strip()

    # Query the first database for rows where the 'title' column starts with the
    # line just read. Use the SQLite LIKE operator for a case-insensitive match.
    # TODO: Only match "<name>"" OR "<name> (*)"
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE title LIKE ?;", (line+'%',))

    # Fetch one row at a time and write XHTML to stdout
    row = cursor.fetchone()
    while row is not None:
        # Process the row
        title = row[1]
        summary = remove_extra_spaces(row[3])
        add_article(title, [summary], line)
        # Fetch the next row
        row = cursor.fetchone()
end_html_document()
# Close the connections to both databases.
conn.close()
