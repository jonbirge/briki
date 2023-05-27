# brikipaedia

## Overview
Just a stupid project to take a list of words and use the Wikipedia API to create an EPUB encyclopedia for offline use (such as on a Kindle).

## Running
To run, you need to have Python 3 installed. Then, you can run the following commands:
    
    ```
    pip install -r reqs.txt
    ./pull_wiki_articles.py
    ./process_db_refs.py
    ./gen_epub.py
    ```

Note that the first script will take a very long time, as it will download the summary of around 50,000 Wikipedia articles and load them into an SQL database. The second script goes through the database and replaces links with SQL table IDs to speed-up subsequent operations. The third function will generate an EPUB file with the articles from a list of titles, defaulting to the list in `level_4_titles.txt`.

## Why?
I decided to do this because I have found myself in situations with poor internet connectivity while reading a book and wanted to look stuff up for background.
