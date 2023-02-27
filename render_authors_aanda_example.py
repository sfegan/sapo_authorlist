# Simple script to generate author list using A&A macros. Meant as an
# example to guide collaborators that might wish to generate author 
# lists in new formats. Internally SAPO uses more sophisticated script
# render_authors_latex.py (see https://github.com/sfegan/sapo_authorlist)

import json
import sys

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

authors = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

with open('authors.tex','w') as fp:
    # Set default stream for print to "fp"
    sys.stdout = fp

    # Note the A&A macros hae a problem generating large author lists. It's 
    # not a problem for the journal version of the paper, as they do the 
    # layout professionally, but it is a problem for manuscripts generated
    # using the macros to be uploaded to astro-ph. Here we use "draft" mode 
    # which seems to fix the layout, but this would not be a solution for the 
    # full paper. For an better solution see "render_authors_latex.py".
    
    print('\\documentclass[longauth,draft]{aa}')
    print('\\begin{document}')
    print('\\title{CTA paper author list}')

    for iauthor,author in enumerate(authors):
        inst = '\\inst{' + ','.join(['\\ref{'+x+'}' for x in author['affil_place_keys']]) + '}'
        linestart = '\\author{' if iauthor==0 else '  \\and '        
        print(linestart+author['author_latex']+inst)
    print('}')
            
    for iaffiliation,affiliation in enumerate(affiliations):
        linestart= '\\institute{' if iaffiliation==0 else '  \\and '
        print(linestart+affiliation['address_latex']+'\\label{'+affiliation['place_key']+'}')
    print('}')

    print('\\maketitle')

    # This line forces the A&A macro to generate the institution list.
    # It would not be needed in a real paper as the list is automatically
    # generated after the references.
    print('\\aainstitutename')
    
    print('\\end{document}')
