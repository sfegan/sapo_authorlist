import json
import html
import unicodedata
import re
import pylatexenc.latexencode
import argparse

def asciify(x):
    return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('utf-8').strip()

def htmlify(x):
    return html.escape(x).encode('ascii', 'xmlcharrefreplace').decode()
#    return x.encode('ascii', 'xmlcharrefreplace').decode('utf8')

def nbspify(x):
    return re.sub('\s+', '&nbsp;', x)

def sig_asciified(sig):
    return asciify(sig)

def sig_latex(sig):
    sig = re.sub('\s+','\u00A0',sig)
    return pylatexenc.latexencode.unicode_to_latex(sig)

def sig_html(sig):
    return nbspify(htmlify(sig))

def short_place_key(short_place_name):
    return re.sub(r'\W+', '', asciify(short_place_name.removeprefix('AffiliationAddress.')))

def format_author_name(firstname, lastname):
    name = ''
    firstname = firstname.strip()
    lastname = lastname.strip()
    name = lastname + ','
    # Split the first name into names
    firstnames = firstname.split()
    for fn in firstnames:
        if fn:        
            if '-' in fn:
                fn = '-'.join(map(lambda hfn: hfn[0] + '.', fn.split('-')))
            else:
                fn = fn[0] + '.'

            name += ' ' + fn
    return name

# ================ #
# Main entry point #
# ================ #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', '-i', default='cta_authors.json', help='Input JSON file name (default: "%(default)s")')
    parser.add_argument('--output', '-o', default='authors.json', help='Output JSON file name (default: "%(default)s")')

    args = parser.parse_args()

    with open(args.input,'r') as fp:
        paper = json.load(fp)

    print(paper['paper_title'])

    sig_map = {}
    for p in paper['authors']:
        pid = p['user']
        
        sig = p['signature']
        fn = p['firstName']
        ln = p['lastName']

        if(sig in sig_map):
            print('WARNING duplicate signature : %s (ids : %s and %s)'%(sig,pid,sig_map[sig]['user']))
        else:
            sig_map[sig] = p
    
        if(not p['affiliations']):
            print('WARNING author has no affiliation :',pid)
        else:
            for a in p['affiliations']:
                if(a != "" and a not in paper['addresses']):
                    print('WARNING author affiliation not found :',pid,a)
                elif(a == ""):
                    print('INFO author affiliation empty :',pid)

        p['alphaName'] = asciify(format_author_name(fn, ln)).lower()

    author_list = dict()
    affiliations_list = []
    author_affiliation_key = dict()
    for p in sorted(paper['authors'], key=lambda x: x['alphaName']):
        ai = p['alphaName']
        sig = p['signature']
        place_ids = []
        place_keys = []
        affil_nums = []
        affil_num_strs = []
        for place_id in p['affiliations']:
            if(place_id and place_id in paper['addresses']):
                place_key = short_place_key(place_id)
                place = paper['addresses'][place_id]
                if(place_id not in author_affiliation_key):
                    author_affiliation_key[place_id] = len(affiliations_list)
                    affiliations_list.append(dict(
                        affil_num            = len(affiliations_list),
                        affil_num_str        = str(len(affiliations_list)+1),
                        place_id             = place_id,
                        place_key            = place_key,
                        short_name_asciified = asciify(place['shortName']),
                        short_name_unicode   = place['shortName'],
                        short_name_xml       = htmlify(place['shortName']),
                        short_name_latex     = pylatexenc.latexencode.unicode_to_latex(place['shortName']),
                        country              = place['country'],
                        address_asciified    = asciify(place['address']),
                        address_unicode      = place['address'],
                        address_xml          = htmlify(place['address']),
                        address_latex        = pylatexenc.latexencode.unicode_to_latex(place['address'])
                    ))
                place_ids.append(place_id)
                place_keys.append(place_key)
                affil_nums.append(author_affiliation_key[place_id])
                affil_num_strs.append(str(author_affiliation_key[place_id]+1))
                ai += ", %06d"%author_affiliation_key[place_id]
        
        author_list[ai] = dict(
            author_id           = p['user'],
            lastname_asciified  = asciify(p['lastName']),
            lastname_unicode    = p['lastName'],
            lastname_xml        = htmlify(p['lastName']),
            lastname_latex      = pylatexenc.latexencode.unicode_to_latex(p['lastName']),
            firstname_asciified = asciify(p['firstName']),
            firstname_unicode   = p['firstName'],
            firstname_xml       = htmlify(p['firstName']),
            firstname_latex     = pylatexenc.latexencode.unicode_to_latex(p['firstName']),
            email               = p['email'],
            corresponding       = False,
            orcid               = p['orcid'],
            affil_place_ids     = place_ids,
            affil_place_keys    = place_keys,
            affil_nums          = affil_nums,
            affil_num_strs      = affil_num_strs,
            author_sortorder    = p['alphaName'],
            author_asciified    = sig_asciified(sig),
            author_unicode      = sig,
            author_html         = sig_html(sig),
            author_xml          = htmlify(sig),
            author_latex        = sig_latex(sig),
        )
        if p['user'] in paper['corresponding_authors']:
            print("Info corresponding author :", sig)
            author_list[ai]['corresponding'] = True

    comment = \
        "CTA author list in JSON format. Contains an array of authors in order that\n" \
        + "they should be included in the author list (element \"authors\"), and an array\n" \
        + "of places to which the authors are affiliated (element \"affiliations\").\n\n" \
        + "Array \"authors\" :\n" \
        + "- author_id         : Unique identifier of author in SAPO database.\n" \
        + "- lastname          : Last name(s) of author in unicode.\n" \
        + "- firstname         : First name(s) of author in unicode.\n" \
        + "- email             : Email addresses for all authors.\n" \
        + "- corresponding     : Corresponding author.\n" \
        + "- orcid             : ORCID identifier if available (optional).\n" \
        + "- author_sortorder  : Sort key used to order authors names (ascii in format\n" \
        + "                      \"lastname, f. i.\").\n" \
        + "- author_asciified  : Ascii version of author's name (in format \n"\
        + "                      \"F. I. Lastname\", with unicode removed).\n" \
        + "- author_unicode    : Unicode version of author's name in format\n" \
        + "                      \"F. I. Lastname\".\n" \
        + "- author_html       : HTML version of author's name in format\n" \
        + "                      \"F.&nbsp;I.&nbsp;Lastname\".\n" \
        + "- author_latex      : LaTeX version of author's name in format\n" \
        + "                      \"F.~I.~Lastname\".\n" \
        + "- affil_nums        : Array listing positions of authors' affiliations in the\n" \
        + "                      affiliation array (starting at zero).\n" \
        + "- affil_num_strs    : Array listing positions of authors' affiliations in the\n" \
        + "                      affiliation array as string (staring at one).\n" \
        + "- affil_place_keys  : Array of text keys for authors affiliations. Can be used\n" \
        + "                      as a unique but readble key for LaTeX \\ref/\\label pairing\n" \
        + "                      to identify affiliations.\n" \
        + "- affil_place_ids   : Array of numeric identifiers for authors affiliations\n" \
        + "                      corresponding to identifier in the SAPO database \n" \
        + "                      (not recommended for general use).\n\n" \
        + "Array \"affiliations\" :\n" \
        + "- affil_num         : Position of affiliation in the affiliation array\n" \
        + "                      (starting at zero).\n" \
        + "- affil_num_str     : Position of affiliation in the affiliation array as\n" \
        + "                      string (staring at one).\n" \
        + "- place_key         : Text key for affiliation. Can be used as a unique but\n" \
        + "                      readble key for LaTeX \\ref/\\label pairing to identify\n" \
        + "                      affiliations.\n" \
        + "- place_id          : Numeric identifier for affiliation corresponding to \n" \
        + "                      identifier in the SAPO database (not recommended for\n" \
        + "                      general use).\n" \
        + "- short_name_unicode: Short name of place in unicode.\n" \
        + "- short_name_latex  : Short name of place in LaTeX format.\n" \
        + "- country           : Country.\n" \
        + "- address_asciified : Ascii version of address (with unicode removed).\n" \
        + "- address_unicode   : Unicode version of address.\n" \
        + "- address_html      : HTML version of address with unicode escaped.\n" \
        + "- address_latex     : LaTeX version of address with unicode escaped.\n"

    author_affiliation_list = dict(
        _comment        = comment,
        title_unicode   = paper['paper_title'],
        title_xml       = htmlify(paper['paper_title']),
        title_latex     = pylatexenc.latexencode.unicode_to_latex(paper['paper_title']),
        title_asciified = asciify(paper['paper_title']),
        date            = paper['date'],
        authors         = [author_list[x] for x in sorted(author_list)],
        affiliations    = affiliations_list
    )

    with open(args.output,'w') as fp:
        json.dump(author_affiliation_list,fp,indent=4)

    print('')
    print("Number of authors:",len(author_list))
    print("Number of affiliations:",len(affiliations_list))