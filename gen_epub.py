#!/usr/bin/env python

import json
import sqlite3
import sys
import time
import os
import re
from ebooklib import epub
from datetime import datetime


### Parameters
ARTICLE_TABLE = "articles"
DB_FILE = "briki.db"


### Functions

def begin_html_document(title):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>
    """

def add_article_link(title, id):
    return f'<p><a href="article_{id}.html">{title}</a></p>'

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

def add_content_paragraphs(paragraphs):
    str = ""
    for paragraph in paragraphs:
        str += f'''
        <p>{paragraph}<br></p>
        '''
    return str

def add_paragraph(text):
    return f"<p>{text}</p>"

def end_html_document():
    return """
<footer>
<p>©2023, all rights reserved.</p>
</footer>
</body>
</html>
    """

# Remove extra white space in string.
def remove_extra_spaces(string):
    return re.sub(r"\s+", " ", string)

# Take a string with newline characters and return a list of paragraphs.
def split_into_paragraphs(string):
    return string.split("\n")


### Open database

# If no database name is provided, use the default.
if len(sys.argv) != 2:
    db_name = DB_FILE
else:
    db_name = sys.argv[1]

# Connect to the database.
conn = sqlite3.connect(db_name)
cursor = conn.cursor()


### Create epub book

book = epub.EpubBook()

book.set_identifier("id123456")
book.set_title("Brikipaedia")
book.set_language("en")
book.add_author("A cast of thousands")

book.spine = ["nav"]

# css_name = "epub_styles.css"
# css_file = open(css_name)
# css_style = css_file.read()
# css_file.close()

db_mod_time = os.path.getmtime(db_name)
db_mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(db_mod_time))
num_articles = cursor.execute(f"SELECT COUNT(*) FROM {ARTICLE_TABLE};").fetchone()[0]
title_page = epub.EpubHtml(title="Title Page", file_name="title_page.xhtml")
title_html = begin_html_document("Title Page")
title_html += "<h1>Brikipaedia</h1>"
title_html += add_paragraph(f"Updated {db_mod_time}")
title_html += add_paragraph(f"This edition contains {num_articles} articles")
title_html += end_html_document()
title_page.content = title_html
book.add_item(title_page)
book.spine.append(title_page)
book.toc.append(epub.Link("title_page.xhtml", "Title Page", "title_page"))


### Add articles

# Read every row from the "articles" table.
cursor.execute(f"SELECT * FROM {ARTICLE_TABLE};")

# Open index.html file for writing.
# TODO: Sort the index entries. Perhaps best done in SQL ahead of time...
index_page = epub.EpubHtml(title="Article Index", file_name="index.xhtml")
index_xhtml = begin_html_document("Index of articles")
index_xhtml += "<h1>Index of articles</h1>"

# Read from the standard input, one line at a time.
n = 0
row = cursor.fetchone()
while row is not None:
    n += 1
    if n % 1000 == 0:
        print("Generated %d articles" % n, file=sys.stderr)


    # Process the row and update index.
    id = row[0]
    title = row[1]
    index_xhtml += add_article_link(title, id)

    # Generate article page
    article_page = epub.EpubHtml(title=title, file_name=f"article_{id}.xhtml")
    summary = row[3]
    summary_pars = split_into_paragraphs(summary)
    html_str = begin_html_document(title)
    html_str += add_article(title, summary_pars)
    html_str += end_html_document()
    article_page.content = html_str
    book.add_item(article_page)
    book.spine.append(article_page)
    book.toc.append(epub.Link(f"article_{id}.xhtml", title, f"article_{id}"))

    # Fetch the next row
    row = cursor.fetchone()

# Finish the index file.
index_xhtml += end_html_document()
index_page.content = index_xhtml
book.add_item(index_page)
book.spine.append(index_page)
book.toc.append(epub.Link("index.xhtml", "Index", "index"))


### Finish book

print("Generating epub navigation...", file=sys.stderr)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
print("Writing epub file...", file=sys.stderr)
epub.write_epub("brikipaedia.epub", book)
