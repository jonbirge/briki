#!/usr/bin/env python

import re
import sqlite3
import sys
import os
import json
import time


### Parameters
ARTICLES_TABLE = 'articles'
TOC_TABLE = 'contents'

### Functions


def begin_html_document():
     return '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Table of Contents</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<center>
<h1>Table of Contents</h1>
    '''

def add_link(title, link):
    return f'<p><a href="{link}">{title}</a></p>'

def add_paragraph(text):
    return f'<p>{text}</p>'

def end_html_document():
    return '''
<footer>
<p>©2023 Briki. All rights reserved.</p>
</footer>
</center>
</body>
</html>
    '''

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

# Get the modification date of the database as a human-readable string.
db_mod_time = os.path.getmtime(db_name)
db_mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(db_mod_time))

# Get the number of articles in the database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute(f"SELECT COUNT(*) FROM {ARTICLES_TABLE};")
num_articles = cursor.fetchone()[0]

# Get the number of rows in the toc table.
cursor.execute(f"SELECT COUNT(*) FROM {TOC_TABLE};")
num_toc_rows = cursor.fetchone()[0]

# Open the output file.
file = open_file_with_dir_creation("./html/index.html")

html_str = begin_html_document()

html_str += add_paragraph(f"Last updated: {db_mod_time}")
html_str += add_paragraph(f"This edition contains {num_articles} \
                          articles referenced by a dictionary of {num_toc_rows} words.")

html_str += add_link("Article List", "articles/index.html")
html_str += add_link("Word Index", "index/index.html")

html_str += end_html_document()
file.write(html_str)

# Write to file.
file.close()
    
# Close the connections to both databases.
conn.close()
