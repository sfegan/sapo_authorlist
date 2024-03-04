# Simple script to generate a comma-separated list of author names

import json
import sys

json_file = sys.argv[1] if len(sys.argv)>1 else 'authors.json'
with open(json_file,'r') as fp:
    author_affiliation_list = json.load(fp)

authors = author_affiliation_list['authors']

for iauthor,author in enumerate(authors):
    print(author['author_unicode']+",")