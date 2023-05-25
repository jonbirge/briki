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
TITLE_FILE = "level_4_titles.txt"
# WORD_FILE = "level_5_titles.txt"

### Functions

def begin_html_document(title):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="styles.css">
<title>{title}</title>
</head>
<body>
    """

def add_index_link(title, id):
    return f'<p><a href="article_{id}.xhtml">{title}</a></p>'

def add_article(title, content):
    str = f"""
<h1>{title}</h1>
    """
    str += add_content_paragraphs(content)
    str += """
    """
    return str

def add_content_paragraphs(paragraphs):
    str = ""
    for paragraph in paragraphs:
        str += f'''
        <p>{paragraph}</p>
        '''
    return str

def add_paragraph(text):
    return f"<p>{text}</p>"

def end_html_document():
    return """
</body>
</html>
    """

# Return a version of "text" with bold HTML tags around ONLY the first instance of "word".
def bold_word(text, word):
    try:
        text_out = re.sub(word, f"<b>{word}</b>", text, flags=re.IGNORECASE, count=1)
    except Exception as e:
        print("Error bolding word %s: %s" % (word, e), file=sys.stderr)
        text_out = text
    return text_out

# Remove any parentheses and their contents from "text"
def remove_parentheses(text):
    return re.sub(r"\(.*?\)", "", text)

# Remove extra white space in string.
def remove_extra_spaces(string):
    return re.sub(r"\s+", " ", string)

# Take a string with newline characters and return a list of paragraphs.
def split_into_paragraphs(string):
    return string.split("\n")

# Remove HTML tags using regular expressions
def remove_html_tags(text):
    clean_text = re.sub('<.*?>', '', text)
    return clean_text


### Open database

# If no word file is provided, use none.
if len(sys.argv) != 2:
    title_file_name = TITLE_FILE
else:
    title_file_name = sys.argv[1]

# Connect to the database.
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()


### Create epub book

book = epub.EpubBook()

book.set_identifier("id123456")
book.set_title("Brikipaedia")
book.set_language("en")
book.add_author("Jonathan Birge")

css = open("styles.css").read()
style = epub.EpubItem(uid='style_css', file_name='style.css', media_type='text/css', content=css)
book.add_item(style)

book.spine = ["nav"]

db_mod_time = os.path.getmtime(DB_FILE)
db_mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(db_mod_time))
num_articles = cursor.execute(f"SELECT COUNT(*) FROM {ARTICLE_TABLE};").fetchone()[0]
title_page = epub.EpubHtml(title="Title Page", file_name="title_page.xhtml")
title_html = begin_html_document("Title Page")
title_html += "<h1>Brikipaedia</h1>"
title_html += add_paragraph(f"Updated {db_mod_time}")
title_html += add_paragraph(f"This edition contains {num_articles} articles.")
title_html += end_html_document()
title_page.content = title_html
book.add_item(title_page)
book.spine.append(title_page)
book.toc.append(epub.Link("title_page.xhtml", "Title Page", "title_page"))


### Add articles

# Read rows from the "articles" table.
if title_file_name is None:
    cursor.execute(f"SELECT * FROM {ARTICLE_TABLE};")
else:
    title_file = open(title_file_name, "r")
    titles = title_file.readlines()
    title_file.close()
    titles = [title.strip() for title in titles]
    cursor.execute(f"SELECT * FROM {ARTICLE_TABLE} WHERE title IN ({','.join('?' for _ in titles)});", titles)

# Open index.html file for writing.
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
    index_xhtml += add_index_link(title, id)

    # Generate article page
    try:
        article_page = epub.EpubHtml(title=title, file_name=f"article_{id}.xhtml")
        summary = remove_html_tags(row[3])
        summary = bold_word(summary, remove_parentheses(title))
        summary_pars = split_into_paragraphs(summary)
        html_str = begin_html_document(title)
        html_str += add_article(title, summary_pars)
        html_str += end_html_document()
        article_page.content = html_str
        book.add_item(article_page)
        book.spine.append(article_page)
        book.toc.append(epub.Link(f"article_{id}.xhtml", title, f"article_{id}"))
    except Exception as e:
        print("Error generating article %d: %s" % (id, e), file=sys.stderr)

    # Fetch the next row
    row = cursor.fetchone()

# Finish the index file.
index_xhtml += end_html_document()
index_page.content = index_xhtml
#book.add_item(index_page)
#book.spine.append(index_page)
#book.toc.append(epub.Link("index.xhtml", "Index", "index"))


### Finish book

print("Generating epub navigation...", file=sys.stderr)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
print("Writing epub file...", file=sys.stderr)
epub.write_epub("brikipaedia.epub", book)
