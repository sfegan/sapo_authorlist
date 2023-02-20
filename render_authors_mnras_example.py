import json

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

author_list = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

with open('authors_mnras.tex','w') as fp:
    print('\\documentclass{mnras}',file=fp)
    print('\\usepackage{enumitem}',file=fp)
    print('\\usepackage[T1]{fontenc}',file=fp)
    print('\\title{Draft LMC paper author list}',file=fp)

    print('\\author['+author_list[0]['author_latex']+' et al]{\parbox{\\textwidth}{\\raggedright\\normalsize%',file=fp)
    for ia,author in enumerate(author_list):
        inst = '$^{' + ','.join(['\\ref{AFFIL::'+x+'}' for x in author['affil_place_keys']]) + '}$'
        print('  '+author['author_latex']+inst,file=fp)
    print('\\newline\\newline\n\\emph{Affiliations can be found at the end of the article}}}',file=fp)
            
    print('\\begin{document}',file=fp)
    print('\\maketitle',file=fp)

    print('\n\\section*{Affiliations}',file=fp)
    print('\\begin{enumerate}[label=$^{\\arabic*}$,ref=\\arabic*,leftmargin=1.5em,labelsep=0.25em,labelwidth=1.25em]',file=fp)
    for ia,affil in enumerate(affiliations):
        print('\\item '+affil['address_latex']+'\\label{AFFIL::'+affil['place_key']+'}',file=fp)
    print('\\end{enumerate}',file=fp)

    print('\\end{document}',file=fp)