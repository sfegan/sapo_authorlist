import json
import sys
import argparse

class LatexRenderer:
    def __init__(self, document_class="article", class_options=None) -> None:
        self.document_class = document_class
        self.class_options = class_options

    def setup_class(self):
        if(self.class_options):
            print('\\documentclass[',self.class_options,']{',self.document_class,'}',sep='')
        else:
            print('\\documentclass{',self.document_class,'}',sep='')
        print('\\usepackage{enumitem}')
        print('\\usepackage[T1]{fontenc}')

    def begin_document(self, title = "CTA paper author list"):
        print('\\title{',title,'}',sep='')
        print('\n\\begin{document}')

    def generate_title_pages(self):
        print('\\maketitle')

    def end_document(self):
        print('\n\\end{document}')

    def start_author_block(self, authors, affiliations):
        pass

    def author(self, iauthor, author):
        pass

    def affiliation_in_author_block(self, iaffiliation, affiliation):
        pass

    def end_author_block(self):
        pass

    def start_affiliations_section(self, affiliations):
        pass

    def affiliation_in_section(self, iaffiliation, affiliation):
        pass

    def end_affiliations_section(self):
        pass

class MNRASLatexRenderer(LatexRenderer):
    def __init__(self, document_class="mnras", class_options=None) -> None:
        super().__init__(document_class)
        self.email_list = []

    def start_author_block(self, authors, affiliations):
        print('\n\\author['+authors[0]['author_latex']+' et al]{\parbox{\\textwidth}{\\raggedright\\normalsize%')

    def author(self, iauthor, author):
        inst = ['\\ref{AFFIL::'+x+'}' for x in author['affil_place_keys']]
        inst = '$^{' + ','.join(inst) + '}$'
        if author['corresponding'] and 'email' in author:
            inst += '\\ref{CONTACTAUTHOR::'+str(len(self.email_list)+1)+'}'
            self.email_list.append('\\url{'+author['email']+'} ('+author['author_latex']+')')
        print('  ',author['author_latex'],inst,sep='')

    def end_author_block(self):
        print('\\newline\\newline\n\\emph{Affiliations can be found at the end of the article}}}')

    def generate_title_pages(self):
        super().generate_title_pages()
        for iemail, email in enumerate(self.email_list):
            print('\\footnotetext[',str(iemail+1),']{',email,
                  '\\label{CONTACTAUTHOR::',str(iemail+1),'}}',sep='')

    def start_affiliations_section(self, affiliations):
        print('\n\\section*{Affiliations}')
        print('\\begin{enumerate}[label=$^{\\arabic*}$,ref=\\arabic*,leftmargin=1.5em,labelsep=0.25em,labelwidth=1.25em]')

    def affiliation_in_section(self, iaffiliation, affiliation):
        print('\\item ',affiliation['address_latex'],
              '\\label{AFFIL::',affiliation['place_key'],'}',sep='')

    def end_affiliations_section(self):
        print('\\end{enumerate}')

class AALatexRenderer(LatexRenderer):
    def __init__(self, astroph=False, orcid=False, document_class="aa", class_options="longauth") -> None:
        self.astroph = astroph
        self.orcid = orcid
        super().__init__(document_class, class_options)

    def setup_class(self):
        super().setup_class()
        print('\\usepackage{txfonts}')

    def generate_title_pages(self):
        super().generate_title_pages()
        if self.astroph:
            print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('% Note : this suppresses generation of the institution list after the')
            print('% bibliography, as in this "astroph" mode we generate the list ourselves.')
            print('% This must be kept in the document submitted to astroph.')
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('\\makeatletter\\aa@longauthfalse\\makeatother')


    def author(self, iauthor, author):
        linestart = '\\author{\\normalsize ' if iauthor==0 else '  \\and '
        inst = ['\\ref{AFFIL::'+x+'}' for x in author['affil_place_keys']]
        if self.astroph:
            inst = '$^{' + ','.join(inst) + '}$'
        else:
            inst = '\\inst{' + ','.join(inst) + '}'
        if author['corresponding'] and 'email' in author:
            inst += '\\thanks{\\url{'+author['email']+'} ('+author['author_latex']+')}'
        if self.orcid and 'orcid' in author and author['orcid']:
            inst += '\\orcid{' + author['orcid'] + '}'
        print(linestart,author['author_latex'],inst,sep='')

    def affiliation_in_author_block(self, iaffiliation, affiliation):
        if not self.astroph:
            linestart= '}\n\n\\institute{' if iaffiliation==0 else '  \\and '
            print(linestart,'{',affiliation['address_latex'],' ',
                '\\label{AFFIL::',affiliation['place_key'],'}}',sep='')

    def end_author_block(self):
        print('}')

    def start_affiliations_section(self, affiliations):
        if self.astroph:
            print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('% Note : in this "astroph" mode we generate the affiliation list ourselves.')
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('\\section*{Affiliations}')
            print('\\begin{enumerate}[label=$^{\\arabic*}$,ref=\\arabic*,leftmargin=1.5em,labelsep=0.25em,labelwidth=1.25em]')
        else:
            print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('% Note : this forces AA macros to output institutes without there being,')
            print('% a bibliography present, it would not be needed in a real AA paper.')
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print('\\kern6pt\\hrule\\kern6pt\\aainstitutename')

    def affiliation_in_section(self, iaffiliation, affiliation):
        if self.astroph:
            print('\\item ',affiliation['address_latex'],
                '\\label{AFFIL::',affiliation['place_key'],'}',sep='')

    def end_affiliations_section(self):
        if self.astroph:
            print('\\end{enumerate}')


# ================ #
# Main entry point #
# ================ #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--render', default='mnras',
                        choices=['mnras', 'aa', 'aa-astroph'],
                        help='LaTeX class to use (default: "%(default)s")')
    parser.add_argument('--mnras', action='store_true', help='Generate LaTeX using MNRAS macros')
    parser.add_argument('--title', '-t', default='CTA paper draft author list', help='Title for LaTeX document')
    parser.add_argument('--suppress_summary', action='store_true', help='Suppress SAPO summary information')
    parser.add_argument('--orcid', action='store_true', help='Output ORCID identities for authors where they are available and supported by the LaTeX style')
    parser.add_argument('--input', '-i', default='authors.json', help='Input JSON file name (default: "%(default)s")')
    parser.add_argument('--output', '-o', default='authors.tex', help='Output LaTeX file name (default: "%(default)s")')

    args = parser.parse_args()

    with open(args.input,'r') as fp:
        author_affiliation_list = json.load(fp)

    authors = author_affiliation_list['authors']
    affiliations = author_affiliation_list['affiliations']

    render = None
    if(args.render == 'mnras'):
        render = MNRASLatexRenderer()
    elif(args.render == 'aa'):
        render = AALatexRenderer(orcid=args.orcid)
    elif(args.render == 'aa-astroph'):
        render = AALatexRenderer(astroph=True,orcid=args.orcid)

    with open(args.output,'w') as fp:
        # Set default stream for print to "fp"
        sys_stdout = sys.stdout
        sys.stdout = fp

        render.setup_class()

        render.start_author_block(authors, affiliations)
        for iauthor,author in enumerate(authors):
            render.author(iauthor, author)
        for iaffiliation,affiliation in enumerate(affiliations):
            render.affiliation_in_author_block(iaffiliation, affiliation)
        render.end_author_block()

        render.begin_document(args.title)
        render.generate_title_pages()

        if(not args.suppress_summary):
            print('\n\\section*{Corrections}\n')
            print('\\flushleft If your details are incorrect on this author list, please let us know using the')
            print('\\href{https://forms.gle/884xVd46H7XtJbaR6}{\\hypersetup{linkcolor=blue} SAPO change of name and affiliation form}\\footnote{\\url{https://forms.gle/884xVd46H7XtJbaR6}}.')
            print('\\textbf{Note}, you cannot opt-in to the author list using this form.')

        render.start_affiliations_section(affiliations)
        for iaffiliation,affiliation in enumerate(affiliations):
            render.affiliation_in_section(iaffiliation, affiliation)
        render.end_affiliations_section()
        
        if(not args.suppress_summary):
            # Add table giving number of authors per country
            print('\n\\section*{Authors by country}\n')
            print('Number of authors:',len(authors),'\\\\')
            print('Number of affiliations:',len(affiliations))
            country_count = dict()
            for author in authors:
                for country in [affiliations[id]['country'] for id in author['affil_nums']]:
                    country_count[country] = country_count.get(country, 0) + 1/len(author['affil_nums'])
            print('\n\\begin{tabbing}')
            print('\\textbf{United Kingdom UK} \\= 8888.8 \\= \\kill')
            for k in sorted(country_count,key=lambda x:country_count[x],reverse=True):
                print('\\textbf{%s} \\> %g \\> %.1f\\%%\\\\'%(k,int(country_count[k]*10)/10, country_count[k]/len(authors)*100))
            print('\\end{tabbing}')

            # Add table giving list of authors per institution, to aid in verification
            # of author eligibility
            print('\n\\section*{Authors by affiliation}\n')
            place_person = dict()
            for author in authors:
                for id in author['affil_nums']:
                    if id not in place_person:
                        place_person[id] = [].copy()
                    place_person[id].append(author['author_latex'])
            print('\\begin{enumerate}[label=\\arabic*]')
            for id,affil in enumerate(affiliations):
                print('\\item \\textbf{%s}:'%affil['short_name_latex'],', '.join(place_person[id]))
            print('\\end{enumerate}')

        render.end_document()
