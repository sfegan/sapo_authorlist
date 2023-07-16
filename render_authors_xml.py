import json
import sys
import argparse

# ================ #
# Main entry point #
# ================ #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--publication_reference', '-r', default='', help='Publication reference for document')
    parser.add_argument('--input', '-i', default='authors.json', help='Input JSON file name (default: "%(default)s")')
    parser.add_argument('--output', '-o', default='authors.xml', help='Output LaTeX file name (default: "%(default)s")')

    args = parser.parse_args()

    with open(args.input,'r') as fp:
        paper = json.load(fp)

    authors = paper['authors']
    affiliations = paper['affiliations']

    with open(args.output,'w') as fp:
        # Set default stream for print to "fp"
        sys_stdout = sys.stdout
        sys.stdout = fp

        print('<?xml version="1.0" encoding="UTF-8"?>')
        print('<!DOCTYPE collaborationauthorlist SYSTEM "author.dtd">')
        print()
        print('<collaborationauthorlist')
        print('   xmlns:foaf="http://xmlns.com/foaf/0.1/"')
        print('   xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/">')
        print()
        print('   <cal:creationDate>%s</cal:creationDate>'%paper['date'])
        if(args.publication_reference and args.publication_reference != ""):
            print('   <cal:publicationReference>%s</cal:publicationReference>'%args.publication_reference)
        else:
            print('   <cal:publicationReference>%s</cal:publicationReference>'%paper['title_xml'])
        print()
        print('   <cal:collaborations>')
        print('      <cal:collaboration id="cta">')
        print('         <foaf:name>CTA</foaf:name>')
        print('      </cal:collaboration>')
        print('   </cal:collaborations>')

        print('   <cal:organizations>')
        for iaffiliation,affiliation in enumerate(affiliations):
            print('      <foaf:Organization id="%s">'%affiliation['place_key'])
            print('         <foaf:name>%s</foaf:name>'%affiliation['short_name_xml'])
            print('         <cal:orgAddress>%s</cal:orgAddress>'%affiliation['address_xml'])
            print('      </foaf:Organization>')
        print('   </cal:organizations>')

        print('   <cal:authors>')
        for iauthor,author in enumerate(authors):
            print('      <foaf:Person>')
            print('         <foaf:name>%s %s</foaf:name>'%(author['firstname_xml'],author['lastname_xml']))
            print('         <foaf:givenName>%s</foaf:givenName>'%author['firstname_xml'])
            print('         <foaf:familyName>%s</foaf:familyName>'%author['lastname_xml'])
            print('         <cal:authorNamePaper>%s</cal:authorNamePaper>'%author['author_xml'])
            print('         <cal:authorCollaboration collaborationid="cta" />')
            print('         <cal:authorAffiliations>')
            for place_key in author['affil_place_keys']:
                print('            <cal:authorAffiliation organizationid="%s" />'%place_key)
            print('         </cal:authorAffiliations>')
            print('         <cal:authorids>')
            if 'orcid' in author and author['orcid']:
                print('            <cal:authorid source="ORCID">%s</cal:authorid>'%author['orcid'].removeprefix('https://orcid.org/'))
            print('         </cal:authorids>')
            print('      </foaf:Person>')
        print('   </cal:authors>')
        print('</collaborationauthorlist>')
#        for iauthor,author in enumerate(authors):
#            render.author(iauthor, author)
#        for iaffiliation,affiliation in enumerate(affiliations):
#            render.affiliation_in_author_block(iaffiliation, affiliation)
