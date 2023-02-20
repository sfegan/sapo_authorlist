import json

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

author_list = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

email_list = []

with open('authors_mnras.tex','w') as fp:
    print('\\documentclass{mnras}',file=fp)
    print('\\usepackage{enumitem}',file=fp)
    print('\\usepackage[T1]{fontenc}',file=fp)
    print('\\title{Draft LMC paper author list}',file=fp)

    print('\\author['+author_list[0]['author_latex']+' et al]{\parbox{\\textwidth}{\\raggedright\\normalsize%',file=fp)
    for ia,author in enumerate(author_list):
        inst = ['\\ref{AFFIL::'+x+'}' for x in author['affil_place_keys']]
        inst = '$^{' + ','.join(inst) + '}$'
        if 'email' in author:
            inst += '\\ref{CONTACTAUTHOR::'+str(len(email_list)+1)+'}'
            email_list.append('\\url{'+author['email']+'} ('+author['author_latex']+')')
        print('  '+author['author_latex']+inst,file=fp)
    print('\\newline\\newline\n\\emph{Affiliations can be found at the end of the article}}}',file=fp)
            
    print('\\begin{document}',file=fp)
    print('\\maketitle',file=fp)
    for iemail, email in enumerate(email_list):
        print('\\footnotetext['+str(iemail+1)+']{'+email+'\\label{CONTACTAUTHOR::'+str(iemail+1)+'}}',file=fp)

    print('\n\\section*{Affiliations}',file=fp)
    print('\\begin{enumerate}[label=$^{\\arabic*}$,ref=\\arabic*,leftmargin=1.5em,labelsep=0.25em,labelwidth=1.25em]',file=fp)
    for ia,affil in enumerate(affiliations):
        print('\\item '+affil['address_latex']+'\\label{AFFIL::'+affil['place_key']+'}',file=fp)
    print('\\end{enumerate}',file=fp)

    print('\n\\section*{Authors by country}\n',file=fp)
    print('Number of authors:',len(author_list),'\\\\',file=fp)
    print('Number of affiliations:',len(affiliations),file=fp)
    country_count = dict()
    for author in author_list:
        for country in [affiliations[id]['country'] for id in author['affil_nums']]:
            country_count[country] = country_count.get(country, 0) + 1/len(author['affil_nums'])
    print('\n\\begin{tabbing}',file=fp)
    print('\\textbf{United Kingdom UK} \\= 8888.8 \\= \\kill',file=fp)
    for k in sorted(country_count,key=lambda x:country_count[x],reverse=True):
        print('\\textbf{%s} \\> %g \\> %.1f\\%%\\\\'%(k,int(country_count[k]*10)/10, country_count[k]/len(author_list)*100),file=fp)
    print('\\end{tabbing}',file=fp)

    print('\n\\section*{Authors by affiliation}\n',file=fp)
    place_person = dict()
    for author in author_list:
        for id in author['affil_nums']:
            if id not in place_person:
                place_person[id] = [].copy()
            place_person[id].append(author['author_latex'])
    print('\\begin{enumerate}[label=\\arabic*]',file=fp)
    for id,affil in enumerate(affiliations):
        print('\\item \\textbf{%s}:'%affil['short_name_latex'],', '.join(place_person[id]),file=fp)
    print('\\end{enumerate}',file=fp)

    print('\\end{document}',file=fp)
