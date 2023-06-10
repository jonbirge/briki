#!/usr/bin/env python

import json
import sqlite3
import sys
import time
import os
import re
from ebooklib import epub


### Parameters
MAX_ARTICLES = 100000
DB_FILE = "briki.db"
TITLE_FILE = "level_4_titles.txt"
# TITLE_FILE = "level_5_titles.txt"
ARTICLE_TABLE = "articles"

### Functions

def begin_html_document(title):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<title>{title}</title>
</head>
<body>
    """

def add_article(title, content):
    str = f"""
<h1>{title}</h1>
    """
    str += add_content_paragraphs(content)
    return str

def add_content_paragraphs(paragraphs: list):
    str = ""
    for paragraph in paragraphs:
        str += f'''
<p>{paragraph}</p>
        '''
    return str

def add_paragraph(text):
    return f"<p>{text}</p>"

def add_ref_link(title, id: int):
    return f'<a href="article_{id}.xhtml"><b>{title}</b></a>'

def add_see_also(see_also: list):
    ref_list = []
    for link_tuple in see_also:
        if link_tuple[0] in titles:
            ref_list.append(link_tuple)
    if len(ref_list) > 0:
        str = '''
<h2>See also:</h2>
<p>'''
        for link_tuple in ref_list:
            str += add_ref_link(link_tuple[0], link_tuple[1])
            if link_tuple != ref_list[-1]:
                str += ", "
        str += '</p>'
        return str
    else:
        return ""

def end_html_document():
    return '''
</body>
</html>
    '''

# Return a version of "text" with bold HTML tags around ONLY the first instance of "word".
def bold_word(text: str, word: str):
    try:
        text_out = re.sub(word, f"<b>{word}</b>", text, flags=re.IGNORECASE, count=1)
    except Exception as e:
        print("Error bolding word %s: %s" % (word, e), file=sys.stderr)
        text_out = text
    return text_out

# Remove any parentheses and their contents from "text"
def remove_parentheses(text: str):
    return re.sub(r"\(.*?\)", "", text)

# Remove extra white space in string.
def remove_extra_spaces(text: str):
    return re.sub(r"\s+", " ", text)

# Take a string with newline characters and return a list of paragraphs.
def split_into_paragraphs(text: str):
    return text.split("\n")

# Remove HTML tags
def remove_html_tags(text: str):
    clean_text = re.sub('<.*?>', '', text)
    return clean_text


### Main

## Connect to the database.
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# If no word file is provided, use default.
if len(sys.argv) != 2:
    title_file_name = TITLE_FILE
else:
    title_file_name = sys.argv[1]

## Create epub book
book = epub.EpubBook()
book.set_identifier("id123456")
book.set_title("Brikipaedia")
book.set_language("en")
book.add_author("Jonathan Birge")

# Add CSS file
css = open("styles.css").read()
style = epub.EpubItem(uid='style', file_name='styles.css', media_type='text/css', content=css)
book.add_item(style)

# Read rows from the "articles" table.
title_file = open(title_file_name, "r")
titles = title_file.readlines()
title_file.close()
titles = [title.strip() for title in titles]

# Add title page
db_mod_time = os.path.getmtime(DB_FILE)
db_mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(db_mod_time))
num_articles = len(titles)
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

## Add articles


# Read from the standard input, one line at a time.
n = 0
cursor.execute(f"SELECT * FROM {ARTICLE_TABLE} WHERE title IN ({','.join('?' for _ in titles)});", titles)
row = cursor.fetchone()
while row is not None and n < MAX_ARTICLES:
    n += 1
    if n % 1000 == 0:
        print("Generated %d articles" % n, file=sys.stderr)

    id = row[0]
    title = row[1]

    # Generate article page
    try:
        article_page = epub.EpubHtml(title=title, file_name=f"article_{id}.xhtml")
        summary = remove_html_tags(row[3])
        summary = bold_word(summary, remove_parentheses(title))
        summary_pars = split_into_paragraphs(summary)
        see_also = json.loads(row[4])
        html_str = begin_html_document(title)
        html_str += add_article(title, summary_pars)
        html_str += add_see_also(see_also)
        html_str += end_html_document()
        article_page.content = html_str
        book.add_item(article_page)
        article_page.add_link(href="styles.css", rel="stylesheet", type="text/css")
        book.spine.append(article_page)
        book.toc.append(epub.Link(f"article_{id}.xhtml", title, f"article_{id}"))
    except Exception as e:
        print("Error generating article %d: %s" % (id, e), file=sys.stderr)

    # Fetch the next row
    row = cursor.fetchone()

## Finish book
print("Generating epub navigation...", file=sys.stderr)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
print("Writing epub file...", file=sys.stderr)
epub.write_epub("brikipaedia.epub", book)
