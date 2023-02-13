import json
import csv
import unicodedata
import re
import pylatexenc.latexencode

def asciify(x):
    return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('utf-8').strip()

def htmlify(x):
    return x.encode('ascii', 'xmlcharrefreplace').decode('utf8')

def nbspify(x):
    return re.sub('\s+', '&nbsp;', x)

def author_asciified(firstname,lastname):
    return asciify(re.sub('\s+',' ',firstname+' '+lastname))

def author_unicode(firstname,lastname):
    return re.sub('\s+',' ',firstname+' '+lastname)

def author_latex(firstname,lastname):
    author = re.sub('\s+','\u00A0',firstname+' '+lastname)
    return pylatexenc.latexencode.unicode_to_latex(author)

def author_html(firstname,lastname):
    return nbspify(htmlify(firstname)+' '+htmlify(lastname))

def author_latex(firstname,lastname):
    author = re.sub('\s+','\u00A0',firstname+' '+lastname)
    return pylatexenc.latexencode.unicode_to_latex(author)

def short_place_key(short_place_name):
    return re.sub(r'\W+', '', asciify(short_place_name))

def load_alt_email_csv(filename):
    alt_email = dict()
    with open(filename) as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            if row[0]:
                alt_email[row[0].lower()] = row[1].lower()
    return alt_email

def load_places_rows(rows):
    places = dict()
    short_place_keys = set()
    for row in rows:
        if row[0]:
            if row[0] in places:
                print('Warning : duplicate places id :',row[0])
            key = short_place_key(row[1])
            if(key in short_place_keys):
                i = 2
                while(key+str(i) in short_place_keys):
                    i += 1
                key = key+str(i)
            short_place_keys.add(key)
            places[row[0]] = [key, row[1], row[2], row[3]]
        if '\u200B' in row[3]:
            print("Warning, address contains character U200B :",row[3])
    return places

def load_places_csv(filename):
    with open(filename) as fp:
        csv_reader = csv.reader(fp)
        return load_places_rows(csv_reader)

def load_people_rows(rows):
    people = dict()
    for row in rows:
        if row[0]:
            if row[0] in people:
                print('Warning : duplicate person id :',row[0])
            people[row[0]] = [x.strip() for x in row[1:12]]
    return people

def load_people_csv(filename):
    with open(filename) as fp:
        fp.readline()
        csv_reader = csv.reader(fp)
        return load_people_rows(csv_reader)

def load_signers_rows(rows):
    signers = []
    for row in rows:
        signers.append([row[1], row[2], row[3], row[5]])
    return signers

def load_signers_csv(filename):
    signers = []
    with open(filename) as fp:
        fp.readline()
        csv_reader = csv.reader(fp)
        return load_signers_rows(csv_reader)

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

alt_email = load_alt_email_csv('Copy of CTA_LMC_Optin (Responses) - Alternative email.csv')
places = load_places_csv('Copy of CTA_LMC_Optin (Responses) - Affiliation addresses.csv')
people = load_people_csv('Copy of CTA_LMC_Optin (Responses) - People.csv')
signers = load_signers_csv('Copy of CTA_LMC_Optin (Responses) - Form responses 1.csv')

main_emails = dict()
cta_emails = dict()

for pid in people:
    p = people[pid]
    main_email = p[2].lower()
    cta_email = p[3].lower()

    if(p[7] != format_author_name(p[1],p[0])):
        print('Warning : signature name differs',p[7],"!=",format_author_name(p[1],p[0]))

    if main_email:
        if main_email in main_emails:
            print('Warning : duplicate email address : %s (ids : %s and %s)'%(main_email,pid,main_emails[main_email]))
        main_emails[main_email] = pid


    if(cta_email):
        if cta_email in cta_emails:
            print('Warning : duplicate CTA email address : %s (ids : %s and %s)'%(cta_email,pid,cta_emails[cta_email]))
        cta_emails[cta_email] = pid

    if p[8].strip()=='':
        print('Warning : author has no affiliation ',p[2])
        if p[9] not in places:
            print('Warning : author affiliation not found ',p[2])
        if len(p)>9:
            if p[9] and p[9] not in places:
                print('Warning : author 2nd affiliation not found ',p[2])

        if len(p)>10:
            if p[10] and p[10] not in places:
                print('Warning : author 3rd affiliation not found ',p[2])

authors = set()
for s in signers:
    email = s[0].lower().strip()
    if email in alt_email:
        email = alt_email[email]
    author_id = None
    if email in main_emails:
        author_id = main_emails[email]
    elif email in cta_emails:
        author_id = cta_emails[email]
    if(author_id is None):
        print('Warning : unknown author :',email)
    else:
        n1 = asciify(s[2]).lower().replace('-',' ')
        n2 = asciify(people[author_id][0]).lower().replace('-',' ')
            
        if(n1 not in n2 and n2 not in n1):
            print('Warning : author surname mismatch :',s[2],"!=",people[author_id][0])
        if(author_id in authors):
            print('Info : author already signed ',email)
        else:  
            authors.add(author_id)

author_list = dict()
affiliations_list = []
author_affiliation_key = dict()
for author_id in sorted(authors, key=lambda x: asciify(people[x][7]).lower()):
    ai = asciify(people[author_id][7]).lower()
    place_ids = []
    place_keys = []
    affil_nums = []
    affil_num_strs = []
    for place_id in people[author_id][8:11]:
        if(place_id):
            if(place_id not in author_affiliation_key):
                author_affiliation_key[place_id] = len(affiliations_list)
                affiliations_list.append(dict(
                    affil_num         = len(affiliations_list),
                    affil_num_str     = str(len(affiliations_list)+1),
                    place_id          = place_id,
                    place_key         = places[place_id][0],
                    country           = places[place_id][2],
                    address_asciified = asciify(places[place_id][3]),
                    address_unicode   = places[place_id][3],
                    address_html      = htmlify(places[place_id][3]),
                    address_latex     = pylatexenc.latexencode.unicode_to_latex(places[place_id][3])
                ))
            place_ids.append(place_id)
            place_keys.append(places[place_id][0])
            affil_nums.append(author_affiliation_key[place_id])
            affil_num_strs.append(str(author_affiliation_key[place_id]+1))
            ai += ", %06d"%author_affiliation_key[place_id]
    
    lastname, firstname = people[author_id][7].split(',')
    lastname = lastname.strip()
    firstname = firstname .strip()

    author_list[ai] = dict(
        author_id        = author_id,
        lastname         = people[author_id][0],
        firstname        = people[author_id][1],
        affil_place_ids  = place_ids,
        affil_place_keys = place_keys,
        affil_nums       = affil_nums,
        affil_num_strs   = affil_num_strs,
        author_sortorder = asciify(people[author_id][7]).lower(),
        author_asciified = author_asciified(firstname, lastname),
        author_unicode   = author_unicode(firstname, lastname),
        author_html      = author_html(firstname, lastname),
        author_latex     = author_latex(firstname, lastname),
    )

comment = \
    "CTA author list in JSON format. Contains an array of authors in order that\n" \
    + "they should be included in the author list (element \"authors\"), and an array\n" \
    + "of places to which the authors are affiliated (element \"affiliations\").\n\n" \
    + "Array \"authors\" :\n" \
    + "- author_id         : Unique identifier of author in SAPO database.\n" \
    + "- lastname          : Last name(s) of author in unicode.\n" \
    + "- firstname         : First name(s) of author in unicode.\n" \
    + "- email             : Email addresses for first authors (optional).\n" \
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
    + "- country           : Country.\n" \
    + "- address_asciified : Ascii version of address (with unicode removed).\n" \
    + "- address_unicode   : Unicode version of address.\n" \
    + "- address_html      : HTML version of address with unicode escaped.\n" \
    + "- address_latex     : LaTeX version of address with unicode escaped.\n"

author_affiliation_list = dict(
    _comment     = comment,
    authors      = [author_list[x] for x in sorted(author_list)],
    affiliations = affiliations_list
)

with open('authors.json','w') as fp:
    json.dump(author_affiliation_list,fp,indent=4)

print('')
print("Number of authors:",len(author_list))
print("Number of affiliations:",len(affiliations_list))
