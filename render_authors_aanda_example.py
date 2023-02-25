import json
import sys

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

authors = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

with open('authors.tex','w') as fp:
    # Set default stream for print to "fp"
    sys.stdout = fp

    # Note the A&A macros hae a problem generating large author lists. Here
    # we use "draft" mode to fix it, but this would not be a solution for a
    # real paper. It's not a problem for the journal as they do the layout
    # professionally but it is a problem for manuscripts uploaded to astro-ph.
    
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
