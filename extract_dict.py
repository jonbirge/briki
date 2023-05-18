#!/usr/bin/env python

import re
import sqlite3
import sys
import os


### Parameters
TABLE_NAME = 'articles'


### Functions

# Function to generate file system prefix from an integer ID.
# The prefix is html/X/, where X is the first digit of the ID.
def path_prefix(id):
    number_str = str(id)
    first_digit = number_str[0]
    return f"./html/{first_digit}/"

def begin_html_document():
     return '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Brikipaedia</title>
<link rel="stylesheet" href="../styles.css">
</head>

<body>
    '''

def add_article(title, content):
    str = f'''
<article>
<h1>{title}</h1>
    '''
    str += add_content_paragraphs(content)
    str += '''
</article>
    '''
    return str

def add_content_paragraphs(paragraphs):
    str = ""
    for paragraph in paragraphs:
        str += f'<p>{paragraph}</p>\n'
    return str

def end_html_document():
    return '''
<footer>
<p>©2023 Briki. All rights reserved.</p>
</footer>
</body>
</html>
    '''

def remove_extra_spaces(string):
    return re.sub(r'\s+', ' ', string)

def open_file_with_dir_creation(file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    file = open(file_path, 'w')
    return file


### Main

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = "briki.db"
else:
    db_name = sys.argv[1]

# Connect to the database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Read every row from the "articles" table.
cursor.execute(f"SELECT * FROM {TABLE_NAME};")

# Read from the standard input, one line at a time.
n = 0
row = cursor.fetchone()
while row is not None:
    n += 1
    if n % 1000 == 0:
        print("Generated %d entries" % n, file=sys.stderr)
    
    # Process the row
    id = row[0]
    title = row[1]
    summary = remove_extra_spaces(row[3])
    file_path = f"{path_prefix(id)}{id}.html"

    # Open file for writing.
    file = open_file_with_dir_creation(file_path)

    # Generate page
    html_str = begin_html_document()
    html_str += add_article(title, [summary])
    html_str += end_html_document()

    # Write to file.
    file.write(html_str)
    file.close()

    # Fetch the next row
    row = cursor.fetchone()
    
# Close the connections to both databases.
conn.close()
