#!/usr/bin/env python

import re
import sqlite3
import sys
import os
import json
import time


### Parameters
ARTICLE_TABLE = "articles"
TOC_TABLE = "contents"


### Functions


# Function to generate file system prefix from an integer ID.
def path_prefix(id):
    number_str = str(id)
    first_digit = number_str[0]
    return f"{first_digit}/"


def begin_html_document(title, stylesheet=""):
    if stylesheet == "":
        style_link = ""
    else:
        style_link = f'<link rel="stylesheet" href="{stylesheet}">'
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{style_link}
<title>{title}</title>
</head>
<body>
    """


def add_article(title, content):
    str = f"""
<article>
<h1>{title}</h1>
    """
    str += add_content_paragraphs(content)
    str += """
</article>
    """
    return str


def add_article_tuple_link(article_tuple):
    id = article_tuple[1]
    title = article_tuple[0]
    return f'<a href="../../articles/{path_prefix(id)}{id}.html">{title}</a>'


def add_article_link(title, id):
    return f'<p><a href="{path_prefix(id)}{id}.html">{title}</a></p>'


def add_link(title, link):
    return f'<p><a href="{link}">{title}</a></p>'


def add_content_paragraphs(paragraphs):
    str = ""
    for paragraph in paragraphs:
        str += f"<p>{paragraph}</p>\n"
    return str


def add_paragraph(text):
    return f"<p>{text}</p>"


def end_html_document():
    return """
<footer>
<p>©2023 Briki and others. All rights reserved.</p>
</footer>
</body>
</html>
    """


# Each article is a tuple of (title, id).
def add_index_entry(title, article_list):
    str = f"""
<article>
<h1>{title}</h1>
<div class="links">
    """
    for article in article_list:
        str += add_article_tuple_link(article)
        if article != article_list[-1]:
            str += '<span class="dot"> &#8226; </span>'
    str += """
</div>
</article>
    """
    return str


def remove_extra_spaces(string):
    return re.sub(r"\s+", " ", string)


def open_file_with_dir_creation(file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    file = open(file_path, "w")
    return file


### Open database

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = "briki.db"
else:
    db_name = sys.argv[1]

# Connect to the database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()


### Article files

# Read every row from the "articles" table.
cursor.execute(f"SELECT * FROM {ARTICLE_TABLE};")

# Open index.html file for writing.
# TODO: Sort the index entries. Perhaps best done in SQL.
index_file = open_file_with_dir_creation("html/articles/index.html")
index_file.write(begin_html_document("Index of articles", "../styles.css"))
index_file.write("<h1>Index of articles</h1>\n")

# Read from the standard input, one line at a time.
n = 0
row = cursor.fetchone()
while row is not None:
    n += 1
    if n % 1000 == 0:
        print("Generated %d entries" % n, file=sys.stderr)

    # Process the row and update index.
    id = row[0]
    title = row[1]
    index_file.write(add_article_link(title, id))

    # Open file for writing.
    file_path = f"html/articles/{path_prefix(id)}{id}.html"
    file = open_file_with_dir_creation(file_path)

    # Generate page
    summary = remove_extra_spaces(row[3])
    html_str = begin_html_document(title, "../../../styles.css")
    html_str += add_article(title, [summary])
    html_str += end_html_document()
    file.write(html_str)
    file.close()

    # Fetch the next row
    row = cursor.fetchone()

# Close the index file.
index_file.write(end_html_document())
index_file.close()


### Index files

# Read every row from the "contents" table.
# Each row is a tuple of (word, refs).
# Refs is a list of article IDs in JSON format.
cursor.execute(f"SELECT * FROM {TOC_TABLE};")
toc_list = cursor.fetchall()

# Create index.html file.
index_file = open_file_with_dir_creation("html/words/index.html")
index_file.write(begin_html_document("Word Index", "../styles.css"))
index_file.write("<h1>Word Index</h1>\n")

# loop through all entries in the TOC.
n = 0
for row in toc_list:
    n += 1
    if n % 1000 == 0:
        print("Generated %d entries" % n, file=sys.stderr)

    # Get the word and extract the JSON-encoded list of refs.
    id = row[0]
    title = row[1]
    ref_ids = json.loads(row[2])

    # Write the word index entry to the file.
    # TODO: If there is only one article, link directly to it.
    index_file.write(add_article_link(title, id))

    # Get the titles of all articles in the list of refs.
    articles = []
    for ref_id in ref_ids:
        cursor.execute(f"SELECT title FROM {ARTICLE_TABLE} WHERE id = {ref_id};")
        article_title = cursor.fetchone()[0]
        articles.append((article_title, ref_id))

    # Write the index entry to the file.
    file = open_file_with_dir_creation(f"html/words/{path_prefix(id)}/{id}.html")
    html_str = begin_html_document(title, "../../../styles.css")
    html_str += add_index_entry(title, articles)
    html_str += end_html_document()
    file.write(html_str)
    file.close()

# Close the index.html file.
index_file.write(end_html_document())
index_file.close()


## Main page

# Get the modification date of the database as a human-readable string.
db_mod_time = os.path.getmtime(db_name)
db_mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(db_mod_time))

# Get the number of articles in the database.
cursor.execute(f"SELECT COUNT(*) FROM {ARTICLE_TABLE};")
num_articles = cursor.fetchone()[0]

# Get the number of rows in the toc table.
cursor.execute(f"SELECT COUNT(*) FROM {TOC_TABLE};")
num_toc_rows = cursor.fetchone()[0]

# Open the output file.
file = open_file_with_dir_creation("./html/index.html")

html_str = begin_html_document("Table of Contents", "styles.css")
html_str += """
<contents>
<h1>Table of Contents</h1>
"""
html_str += add_paragraph(f"Last updated: {db_mod_time}")
html_str += add_paragraph(
    f"This edition contains {num_articles} articles referenced by a dictionary of {num_toc_rows} words."
)
html_str += add_link("Article List", "articles/index.html")
html_str += add_link("Word Index", "words/index.html")
html_str += "</contents>"
html_str += end_html_document()
file.write(html_str)

# Write to file.
file.close()

# Copy stylesheet to html directory.
os.system("cp styles.css html/styles.css")

# Close the connection to database.
conn.close()
