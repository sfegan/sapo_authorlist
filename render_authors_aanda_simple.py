import json

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

author_list = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

with open('authors_aanda.tex','w') as fp:
    print('\\documentclass[longauth,draft,bibyear]{aa}',file=fp)
    print('\\begin{document}',file=fp)
    print('\\title{Draft LMC paper author list}',file=fp)

    for ia,author in enumerate(author_list):
        inst = '\\inst{' + ','.join(author['affil_num_strs']) + '}'
        startswith = '\\author{' if ia==0 else '  \\and '        
        print(startswith+author['author_latex']+inst,file=fp)
    print('}',file=fp)
            
    for ia,affil in enumerate(affiliations):
        startwith= '\\institute{' if ia==0 else '  \\and '
        print(startwith+affil['address_latex'],file=fp)
    print('}',file=fp)

    print('\\maketitle',file=fp)
    print('\\begin{thebibliography}{HELLO}',file=fp)
    print('\\bibitem[1]{Fake reference to prompt A&A macro to emit instiutions}',file=fp)
    print('\\end{thebibliography}',file=fp)
    print('\\end{document}',file=fp)
