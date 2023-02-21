import json
import sys

with open('authors.json','r') as fp:
    author_affiliation_list = json.load(fp)

author_list = author_affiliation_list['authors']
affiliations = author_affiliation_list['affiliations']

email_list = []

with open('authors_mnras.tex','w') as fp:
    # Set default stream for print to "fp"
    sys_stdout = sys.stdout
    sys.stdout = fp

    # Print the usual LaTeX header and include packages needed
    print('\\documentclass{mnras}')
    print('\\usepackage{enumitem}')
    print('\\usepackage[T1]{fontenc}')
    print('\\title{Draft LMC paper author list}')

    # Print authors, linking to their affiliations using "\ref".
    # Add footnote symbol for corrresponfing authors using "\ref" to footnote
    # Build list of corresponding authors; used below to generate footnotes
    print('\\author['+author_list[0]['author_latex']+' et al]{\parbox{\\textwidth}{\\raggedright\\normalsize%')
    for ia,author in enumerate(author_list):
        inst = ['\\ref{AFFIL::'+x+'}' for x in author['affil_place_keys']]
        inst = '$^{' + ','.join(inst) + '}$'
        if 'email' in author:
            inst += '\\ref{CONTACTAUTHOR::'+str(len(email_list)+1)+'}'
            email_list.append('\\url{'+author['email']+'} ('+author['author_latex']+')')
        print('  '+author['author_latex']+inst)
    print('\\newline\\newline\n\\emph{Affiliations can be found at the end of the article}}}')

    # Run maketitle macro and generate footnotes for corresponding authors
    # making "\label" targets that are linked to above
    print('\\begin{document}')
    print('\\maketitle')
    for iemail, email in enumerate(email_list):
        print('\\footnotetext['+str(iemail+1)+']{'+email+'\\label{CONTACTAUTHOR::'+str(iemail+1)+'}}')

    # Add paragraph giving SAPO form authros can use correct details
    print('\\flushleft If your details are incorrect on this author list, please let us know using the')
    print('\\href{https://docs.google.com/forms/d/e/1FAIpQLSc2PVP7k_vS-PI80zm-_naTkkqH5IYhaA7_ZO477Ahgt7o4BA/viewform?usp=sf_link}{SAPO change of name and affiliation form}.')
    print('\\textbf{Note}, you cannot opt-in to the author list using this form.')

    # Add affiliations in their own section using enumerate, and generate 
    # "\label"s for author names to link to
    print('\n\\section*{Affiliations}')
    print('\\begin{enumerate}[label=$^{\\arabic*}$,ref=\\arabic*,leftmargin=1.5em,labelsep=0.25em,labelwidth=1.25em]')
    for ia,affil in enumerate(affiliations):
        print('\\item '+affil['address_latex']+'\\label{AFFIL::'+affil['place_key']+'}')
    print('\\end{enumerate}')

    # Add table giving number of authors per country
    print('\n\\section*{Authors by country}\n')
    print('Number of authors:',len(author_list),'\\\\')
    print('Number of affiliations:',len(affiliations))
    country_count = dict()
    for author in author_list:
        for country in [affiliations[id]['country'] for id in author['affil_nums']]:
            country_count[country] = country_count.get(country, 0) + 1/len(author['affil_nums'])
    print('\n\\begin{tabbing}')
    print('\\textbf{United Kingdom UK} \\= 8888.8 \\= \\kill')
    for k in sorted(country_count,key=lambda x:country_count[x],reverse=True):
        print('\\textbf{%s} \\> %g \\> %.1f\\%%\\\\'%(k,int(country_count[k]*10)/10, country_count[k]/len(author_list)*100))
    print('\\end{tabbing}')

    # Add table giving list of authors per institution, to aid in verification
    # of author eligibility
    print('\n\\section*{Authors by affiliation}\n')
    place_person = dict()
    for author in author_list:
        for id in author['affil_nums']:
            if id not in place_person:
                place_person[id] = [].copy()
            place_person[id].append(author['author_latex'])
    print('\\begin{enumerate}[label=\\arabic*]')
    for id,affil in enumerate(affiliations):
        print('\\item \\textbf{%s}:'%affil['short_name_latex'],', '.join(place_person[id]))
    print('\\end{enumerate}')

    # End of document
    print('\\end{document}')
