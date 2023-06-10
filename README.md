# brikipaedia

## Overview
Just a simple project to take a list of words and use the Wikipedia API to create an EPUB encyclopedia for offline use (such as on a Kindle or iPad). It downloads summaries of the 50,000 most important Wikipedia articles (the so-called "level 5" articles) and creates an EPUB based on them. This could also be useful for training LLMs, which was my other motivation.

## Running
To run, you need to have Python 3 installed. Then, you can run the following commands:
    
    pip install -r reqs.txt
    ./pull_wiki_articles.py
    ./process_db_refs.py
    ./gen_epub.py [title_list_file]

Note: the first script will take a *very* long time (a couple days), as it will download the summary of up to 50,000 Wikipedia articles slowly (to stay within API terms of use limits) and load them into an SQL database, along with references to any linked articles. The second script goes through the database and replaces links with SQL table IDs to speed-up subsequent operations. The third function will generate an EPUB file with the articles. You can also specify article lists on the command line to tailor the EPUB.

## Releases
The releases included here include a populated database with the Level 5 article summaries and the final EPUB documents for the top 10,000 and top 50,000 articles, so you don't have to spend a few days downloading them yourself. If you want to mess with this code I recommend grabbing the lastest release and copying in the .db file to your fork.

## Issues
Despite the fact that this creates valid EPUB documents (according to the official EPUB validation code from W3C) I've had a ton of trouble getting these loaded on to my Kindle via the Amazon "Send to Kindle" website. My guess is the table of contents is too large for it to handle, or the file itself is just too big. If anybody finds a solution to this I'd appreciate any help.

## Why?
I decided to do this because I have found myself in situations with poor internet connectivity while reading a book and wanted to look stuff up for background.
