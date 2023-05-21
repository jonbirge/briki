#!/usr/bin/env python

from ebooklib import epub
import os

# Create a new EPUB book
# TODO: Use database to get title
# TODO: Add CSS file and attach to each chapter
print("Creating EPUB book...")
book = epub.EpubBook()

# Set the metadata for the book
book.set_title("Brikipaedia")
book.set_language("en")

html_dir = "./xhtml"

# Recurse through html_dir and add each HTML file to the book
n = 0  # Counter for number of files processed
for root, dirs, files in os.walk(html_dir):
    for filename in files:
        if filename.endswith(".xhtml"):
            n += 1
            file_path = os.path.join(root, filename)
            local_file_path = file_path.replace(html_dir + "/", "")
            chapter = epub.EpubHtml(
                title=filename, file_name=local_file_path, lang="en"
            )
            chapter.content = open(file_path, "r", encoding="utf-8").read()
            book.add_item(chapter)
            if n % 1000 == 0:
                print(f"Processing file {n}: path: {file_path}...")

# Create a table of contents
print("Creating table of contents...")
book.toc = (
    epub.Link(f"{html_dir}/index.xhtml", "Introduction", "intro"),
    epub.Link(f"{html_dir}/index/index.xhtml", "Word Index", "word-index"),
    epub.Link(f"{html_dir}/articles/index.xhtml", "Article List", "article-list"),
)

# Add the table of contents to the book
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Generate the EPUB file
print("Generating EPUB file...")
epub.write_epub("brikipaedia.epub", book, {})
