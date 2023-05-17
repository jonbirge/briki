#!/usr/bin/env python
# 2023-05-16 14:18:05

import re
import sqlite3
import sys
import os
import json


### Parameters
ARTICLES_TABLE = 'articles'
TOC_TABLE = 'contents'

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
<title>Brikipaedia Index</title>
<link rel="stylesheet" href="styles.css">
</head>

<body>
    <h1>Brikipaedia Index</h1>
    '''

# Add index entry for all articles in article_list.
# Each article is a tuple of (title, id).
def add_index_entry(title, article_list):
    str = f'''
<index>
{title}: 
    '''
    for article in article_list:
        str += f'{add_link(article)} '
    str += '''
</index>
    '''
    return str

def add_link(article_tuple):
    id = article_tuple[1]
    title = article_tuple[0]
    return f'<a href="{path_prefix(id)}{id}.html">{title}</a>'

def end_html_document():
    return '''
<footer>
<p>© 2023 Jonathan Birge. All rights reserved.</p>
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

# Read every row from the "contents" table.
# Each row is a tuple of (word, refs).
# Refs is a list of titles in JSON format.
cursor.execute(f"SELECT * FROM {TOC_TABLE};")
toc_list = cursor.fetchall()

# Write TOC HTML file.
file = open_file_with_dir_creation("./html/toc.html")
html_str = begin_html_document()
file.write(html_str)

# loop through all entries in the TOC.
n = 0
for word in toc_list:
    n += 1
    if n % 100 == 0:
        print("Generated %d entries" % n, file=sys.stderr)
    
    # Get the word and extract the JSON-encoded list of refs.
    title = word[1]
    refs = json.loads(word[2])

    # For each ref, get the ID from the "articles" table.
    articles = []
    for ref in refs:
        cursor.execute(f"SELECT id FROM {ARTICLES_TABLE} WHERE title = ?;", (ref,))
        id = cursor.fetchone()[0]
        articles.append((ref, id))
    
    # Write the index entry to the file.
    file.write(add_index_entry(title, articles))

html_str += end_html_document()
file.write(html_str)

# Write to file.
file.close()
    
# Close the connections to both databases.
conn.close()
