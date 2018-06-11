#!/usr/bin/env python

import re

#case_title = "Ian Scott and McMurray and Kristy Dee McMurray"
#case_title = "Ian Scott McMurray and Kristy Dee McMurray"
#case_title = "Ian Scott McMurray and Kristy Dee Morrey"
#case_title = "C.W. Mining Company"
#case_title = "US Oil Sands Inc."
#case_title = "Ian Scott McMurray, LLC"
#case_title = "Ian Scott McMurray"
#case_title = "Ian Scott McMurray, Sr."
#case_title = "Foster v. Mawhinney et al"
#case_title = "John E Harper, Jr. and Janet Harper"
#case_title = "Arturo Morales-Llan, SR"
#case_title = "Vernon L McCalmant, III and Jenny R McCalmant"
#case_title = "Erivan E Dos Santos"
case_title = "Jerrit James O&#039;Berto"

smaller_case_title = ''

case_title_pieces = case_title.split(" and ")
#print('\tBefore: %s'%case_title)
if case_title_pieces:
    if len(case_title_pieces) >= 3: # more than two people/company! limit on size instead
        smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
    elif len(case_title_pieces) == 2:
        # Remove any abbrev after the name (Junior and Senior in this instance)
        case_title_person_1 = re.sub(r', [isj][ir]+.?$', '', case_title_pieces[0], flags=re.I)
        p1 = case_title_person_1.split(" ")
        #p1 = case_title_pieces[0].split(" ")
        p1_first = p1[0]

        # Remove any abbrev after the name (Junior and Senior in this instance)
        case_title_person_2 = re.sub(r', [isj][ir]+.?$', '', case_title_pieces[1], flags=re.I)
        p2 = case_title_person_2.split(" ")
        #p2 = case_title_pieces[1].split(" ")
        p2_first = p2[0]
        if p1[-1] == p2[-1]:
            #smaller_case_title = '%s. & %. %s'% (p1_first[0], p2_first[0], p2[-1])
            smaller_case_title = '%s, %s. &amp; %s.'% (p2[-1], p1_first[0], p2_first[0])
        else:
            #smaller_case_title = '%s. %s & %s. %s'% (p1_first[0], p1[-1], p2_first[0], p2[-1])
            smaller_case_title = '%s, %s. &amp; %s, %s.'% (p1[-1], p1_first[0], p2[-1], p2_first[0])
    else:
        if ',' in case_title_pieces[0]:
            if re.search(r', [isj][ir]+.?$', case_title_pieces[0], flags=re.I): # jr / sr
                # Remove any abbrev after the name (Junior and Senior in this instance)
                case_title_person_1 = re.sub(r', [isj][ir]+.?$', '', case_title_pieces[0], flags=re.I)
                p1 = case_title_person_1.split(" ")
                p1_first = p1[0]
                smaller_case_title = '%s, %s.'% (p1[-1], p1_first[0])
            else:
                smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
        else:
            # Try to determine a name from a company name
            print("c")
            if re.search(r'.*\bcompany|inc|llc[,.]?$', case_title_pieces[0], flags=re.I): # company found
                print('c1')
                smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
            elif re.search(r'.*\sv.\s.*', case_title_pieces[0], flags=re.I): # Adversary
                print('c2')
                smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
            else:
                print('c3')
                p1 = case_title_pieces[0].split(" ")
                p1_first = p1[0]
                #smaller_case_title = '%s. %s'% (p1_first[0], p1[-1])
                smaller_case_title = '%s, %s.'% (p1[-1], p1_first[0])

print smaller_case_title
print len(case_title_pieces)

