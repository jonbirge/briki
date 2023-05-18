#!/usr/bin/env python

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
    return f"./{first_digit}/"

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

# <div class="entry">
# <div class="word">Word 1</div>
# <div class="links">
#     <a href="#">Related Article 1</a>
#     <span class="dot">&#8226;</span>
#     <a href="#">Related Article 2</a>
#     <span class="dot">&#8226;</span>
#     <a href="#">Related Article 3</a>
# </div>
# </div>
# Add index entry for all articles in article_list.
# Each article is a tuple of (title, id).
def add_index_entry(title, article_list):
    str = f'''
<div class="entry">
<div class="word">{title}</div>
<div class="links">
    '''
    for article in article_list:
        str += add_link(article)
        if article != article_list[-1]:
            str += '<span class="dot">&#8226;</span>'
    str += '''
</div>
</div>
    '''
    return str

def add_link(article_tuple):
    id = article_tuple[1]
    title = article_tuple[0]
    return f'<a href="{path_prefix(id)}{id}.html">{title}</a>'

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

# Read every row from the "contents" table.
# Each row is a tuple of (word, refs).
# Refs is a list of article IDs in JSON format.
cursor.execute(f"SELECT * FROM {TOC_TABLE};")
toc_list = cursor.fetchall()

# Write TOC HTML file.
file = open_file_with_dir_creation("./html/toc.html")
html_str = begin_html_document()
file.write(html_str)

# loop through all entries in the TOC.
n = 0
for row in toc_list:
    n += 1
    if n % 1000 == 0:
        print("Generated %d entries" % n, file=sys.stderr)
    
    # Get the word and extract the JSON-encoded list of refs.
    title = row[1]
    ref_ids = json.loads(row[2])

    # Get the titles of all articles in the list of refs.
    articles = []
    for id in ref_ids:
        cursor.execute(f"SELECT title FROM {ARTICLES_TABLE} WHERE id = {id};")
        article_title = cursor.fetchone()[0]
        articles.append((article_title, id))
    
    # Write the index entry to the file.
    file.write(add_index_entry(title, articles))

html_str += end_html_document()
file.write(html_str)

# Write to file.
file.close()
    
# Close the connections to both databases.
conn.close()
