import json
import sys

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

author_list = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

with open('authors.tex','w') as fp:
    # Set default stream for print to "fp"
    sys.stdout = fp

    # Note the A&A macros hae a problem generating large author lists. Here
    # we use "draft" mode to fix it, but this would not be correct for a real
    # paper.
    
    print('\\documentclass[longauth,draft]{aa}')
    print('\\begin{document}')
    print('\\title{CTA paper author list}')

    for ia,author in enumerate(author_list):
        inst = '\\inst{' + ','.join(['\\ref{'+x+'}' for x in author['affil_place_keys']]) + '}'
        startswith = '\\author{' if ia==0 else '  \\and '        
        print(startswith+author['author_latex']+inst)
    print('}')
            
    for ia,affil in enumerate(affiliations):
        startwith= '\\institute{' if ia==0 else '  \\and '
        print(startwith+affil['address_latex']+'\\label{'+affil['place_key']+'}')
    print('}')

    print('\n\\maketitle')

    # This line forces the A&A macro to generate the institution list.
    # It would not be needed in a real paper as the list is automatically
    # generated after the references.
    print('\n\\aainstitutename')
    
    print('\n\\end{document}')
