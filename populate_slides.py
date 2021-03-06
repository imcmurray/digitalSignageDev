#!/usr/bin/env python

from __future__ import print_function
import json,requests,time,random,re
from datetime import date
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from HTMLParser import HTMLParser

todays_hearings_to_be_heard = {}
new_slide_ids = []
judge_inits = ['rkm','wtt','jtm','kra']
# The following should be taken from the spreadsheet (which we have already done in another example)
# Need to pull that logic in here after testing the welcome page
# We have already proven that we can generate slides for each courtroom
# Now we are testing the welcome digital signage creation with the welcome dictionary
judge_courtrooms = {'rkm': '376', 'wtt': '369', 'kra': '369', 'jtm': '341' }
judge_names = {'rkm': 'Chief Judge R. Kimball Mosier', 'wtt': 'Judge William T. Thurman',
        'jtm': 'Judge Joel T. Marker', 'kra': 'Judge Kevin R. Anderson'}
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_'
template_element_groups = ['elem-htime-','elem-cnum-', 'elem-ctitle-','elem-hmatter-','elem-hmovant-']

h = HTMLParser()
today = date.today()
#formatted_today = today.strftime("%Y-%m-%d")
formatted_today = "2018-05-23"
right_now_epoch = int(time.time())


def prepare_name_list(data):
    names = []
    for name in data:

        # Look for joint debtors with different last names
        regex = r",\s\w\.\s\&amp;\s\w\w"
        if len( [i for i in re.finditer(regex, name)]):
            name_pieces = name.split(" &amp; ")
            p1 = name_pieces[0].split(" ")
            p2 = name_pieces[1].split(" ")
            if p1[0] == p2[0]:
                names.append(name)
            else:
                names.append('%s %s'% (p1[0], p1[1]))
                names.append('%s %s'% (p2[0], p2[1]))
        else:
            names.append(name)

    ret_names = []
    for name in names:
        ret_names.append((name[:20] + '...') if len(name) > 23 else name)

    return sorted(set(ret_names))


def update_greeter_svg(data):

    cr_col_pos_index = {}
    for cr in data:
        col = 1
        pos = 1
        #sorted_hearings_per_cr = sorted(set(data[cr]))
        sorted_hearings_per_cr = prepare_name_list(data[cr])
        for name in sorted_hearings_per_cr:
            cr_col_pos = '{{%s-c%s-position%s}}'% (cr, col, pos)
            # If multiple people in case title, we need to split them up for their own line
            # In the case where joint debtors with different last names
            #case_title_pieces = name.split(". & ")
            #regex = r",\s\w\.\s\&amp;\s\w\w"
            #if len( [i for i in re.finditer(regex, name)]):
                #name_pieces = name.split(" &amp; ")
                #print(name)
                #print('\t%s-%s'%(name_pieces[0], name_pieces[1]))
                #p1 = name_pieces[0].split(" ")
                #p2 = name_pieces[1].split(" ")
                #print('\t\tp1 = [%s]'%p1)
                #print('\t\tp2 = [%s]'%p2)
                #if p1[0] == p2[0]:
                #    cr_col_pos_index.setdefault(cr_col_pos,name)
                #else:
                #    cr_col_pos_index.setdefault(cr_col_pos,'%s %s'% (p1[0], p1[1]))
                    # Can we add to the list?
                #    sorted_hearings_per_cr.append('%s %s'% (p2[0], p2[1]))
            #else:

            cr_col_pos_index.setdefault(cr_col_pos,name)

            pos=pos+1
            if pos > 22:
                col = col+1
                pos = 1

    #pprint(cr_col_pos_index)
    updated = []
    with open("welcome-template-05152018-plain.svg") as fin:
        with open("updated-greeter.svg","w") as fout:
            for line in fin:
                #line = line.rstrip()
                line = re.sub(r'(\{\{\d+-c\d-position\d+\}\})', lambda m: cr_col_pos_index.get(m.group()), line)
                #updated.append(line)
                fout.write(line)

    #pprint(updated)

def shorten_case_title(case_title):
    # Sort out the cs_short_title
    # We only want the first init, lastname
    smaller_case_title = ''
    case_title_pieces = case_title.split(" and ")
    if case_title_pieces:
        if len(case_title_pieces) >= 3: # more than two people/company! limit on size instead
            smaller_case_title = case_title
        elif len(case_title_pieces) == 2:
            p1 = case_title_pieces[0].split(" ")
            p1_first = p1[0]
            p2 = case_title_pieces[1].split(" ")
            p2_first = p2[0]
            if p1[-1] == p2[-1]:
                #smaller_case_title = '%s. & %. %s'% (p1_first[0], p2_first[0], p2[-1])
                smaller_case_title = '%s, %s. &amp; %s.'% (p2[-1], p1_first[0], p2_first[0])
            else:
                #smaller_case_title = '%s. %s & %s. %s'% (p1_first[0], p1[-1], p2_first[0], p2[-1])
                smaller_case_title = '%s, %s. &amp; %s, %s.'% (p1[-1], p1_first[0], p2[-1], p2_first[0])
        else:
            if ',' in case_title_pieces[0]:
                smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
            else:
                p1 = case_title_pieces[0].split(" ")
                p1_first = p1[0]
                #smaller_case_title = '%s. %s'% (p1_first[0], p1[-1])
                smaller_case_title = '%s, %s.'% (p1[-1], p1_first[0])
        return smaller_case_title
    else:
        return 'UNKNOWN'


for judge in judge_inits:
    print("Working on Judge [%s]" % judge)
    judge_json_url = "%s%s.json" % (url, judge)

    # JSON extraction
    response = requests.get(judge_json_url)
    json_obj = response.json()

    for k in range(len(json_obj['rows'])):
        inday = json_obj['rows'][k]['id']
        event = json_obj['rows'][k]['value']

        if inday == formatted_today:
            if event['hearing_set'] > right_now_epoch:
                    todays_hearings_to_be_heard.setdefault(judge,{}).setdefault(event['hearing_set'],{})[event['sort_count']] = json.dumps(event);

if not todays_hearings_to_be_heard:
	print('Sorry - no hearings to populate')
else:

    # Setup OAUTH2 scope and connection
    SCOPES = (
	'https://www.googleapis.com/auth/drive',
	'https://www.googleapis.com/auth/presentations',
	'https://www.googleapis.com/auth/spreadsheets',
    )
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	creds = tools.run_flow(flow, store)
    slides_service = build('slides', 'v1', http=creds.authorize(Http()))
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
    sheets_service = build('sheets', 'v4', http=creds.authorize(Http()))

    PRESENTATION_ID = '1CuDcEYKxvJGF1dWQrjnhW3GrPWB6bQxe0cTauKRXWa4'
    TEMPLATE_SLIDE_ID = 'template-table-hearings-slide'
    #presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
    #slides = presentation.get('slides')

    # Work out how many field groupings we need to process
    elements_on_the_page = slides_service.presentations().pages().get(presentationId=PRESENTATION_ID,
            pageObjectId=TEMPLATE_SLIDE_ID).execute().get('pageElements')

    element_template_count = 0
    element_template_index=[]
    for i, element in enumerate(elements_on_the_page):
        if 'elem-htime-' in element['objectId']:
            element_template_count=element_template_count+1
        # Now save each element so we can tell later which ones we need to empty
        if 'elem-' in element['objectId']:
            element_template_index.append(element['objectId'])
 
    req_to_send = []
    elements_to_slide_index = {}
    welcome = {}

    # Now we have active hearings and google connections, update the spreadsheet with data
    for judge, v in todays_hearings_to_be_heard.items():
	print(judge)
        page_id = '%sslide%sd0' % (judge, str(time.strftime('%I%M%p', time.localtime())))
        #page_id = '%sslideb0' % judge
        req_to_send.append({
            "duplicateObject": {
                "objectId": TEMPLATE_SLIDE_ID,
                "objectIds": {
                    TEMPLATE_SLIDE_ID: page_id
                }
            }
        })
        new_slide_ids.append(page_id)
        elements_to_slide_index[page_id]=element_template_index
        watch_element_count = 1

	#for k, v in sorted(todays_hearings_to_be_heard[judge].items(),reverse=True):
	for k, v in sorted(todays_hearings_to_be_heard[judge].items()):
	    block_time = str(time.strftime('%I:%M %p', time.localtime(k))).lstrip('0')
            #print('k=%s'% k)
            # This is the epoch time (in k) v is the list of hearings for the epoch
            # Since we're combining all times for the day (in this script)
            # We need to watch where we left off on the inserts to the copied template
            # Since each list starts at position 0

            last_block_time = ''
            for k1, v1 in v.items():
                if ( watch_element_count <= element_template_count):
                    #print('\tk1=%s|%s/%s'% (k1,watch_element_count,element_template_count))
                    # We just need to walk through the element_template_count and update
                    jonj = json.loads(v1)
                    #for elem_count in range(1, element_template_count):
                    for elem in template_element_groups:
                        replacement_text = ''
                        if elem == 'elem-htime-':
                            if block_time != last_block_time:
                                replacement_text = block_time
                            else:
                                #replacement_text = h.unescape('     &#10149;')
                                replacement_text = h.unescape('      &#10148;')
                            last_block_time = block_time
                        elif elem == 'elem-cnum-':
                            replacement_text = jonj['cs_case_number']
                        elif elem == 'elem-ctitle-':
                            smaller_case_title = shorten_case_title(jonj['cs_short_title'])
                            # Load the full case title into the welcome dictionary
                            welcome.setdefault(judge,{}).setdefault(k,[]).append(smaller_case_title)
                            smaller_case_title = (smaller_case_title[:30] + '...') if len(smaller_case_title) > 33 else smaller_case_title
                            replacement_text = h.unescape(smaller_case_title)
                            # populate the welcome dictionary
                            #welcome.setdefault(judge,{}).setdefault(k,[]).append(replacement_text)
                        elif elem == 'elem-hmatter-':
                            smaller_matter = (jonj['chs_matter'][:84] + '...') if len(jonj['chs_matter']) > 87 else jonj['chs_matter']
                            replacement_text = h.unescape(smaller_matter)
                        elif elem == 'elem-hmovant-':
                            replacement_text = h.unescape(jonj['movant_name'])

                        #element_id = '{{%s%s}}'% (elem, elem_count)
                        element_id = '{{%s%s}}'% (elem, watch_element_count)

                        if replacement_text:
                            #remove the element from the index
                            #print('Removing element_id {%s} from page_id {%s}'% (element_id, page_id))
                            for e in elements_to_slide_index:
                                if e == element_id:
                                    elements_to_slide_index[e].remove(element_id)
#                            elements_to_slide_index[page_id].remove(element_id)

                            # We have some text to show, so add it to the list
                            req_to_send.append({
                                'replaceAllText': {
                                    'containsText': {'text': element_id},
                                    'replaceText': replacement_text,
                                    'pageObjectIds': [ page_id ]
                            }})

                        #print("\t%s (%s|%s) = [%s|%s|%s|%s]\n\t%s (%s|%s)\n" % (
                            #k1, page_id, element_id, jonj['cs_case_number'], jonj['cs_chapter'], jonj['judge_name'],
                            #jonj['cs_short_title'], jonj['chs_matter'], jonj['movant_name'],
                            #jonj['location']
                        #))
                        #toSlide = '%s [%s] %s %s\n%s' % (block_time, k1, jonj['cs_case_number'], jonj['cs_short_title'], jonj['chs_matter'])
                    watch_element_count=watch_element_count+1

        # place timestamp
        req_to_send.append({
            'replaceAllText': {
                'containsText': {'text': '{{last-updated}}'},
                'replaceText': str(time.strftime('%c', time.localtime())),
                'pageObjectIds': [ page_id ]
        }})

        # place courtroom
        req_to_send.append({
            'replaceAllText': {
                'containsText': {'text': '{{courtroom}}'},
                'replaceText': 'COMING SOON!',
                'pageObjectIds': [ page_id ]
        }})

        # place Hearing Date
        req_to_send.append({
            'replaceAllText': {
                'containsText': {'text': '{{hearing-date}}'},
                'replaceText': 'Wednesday May 23rd 2018',
                'pageObjectIds': [ page_id ]
        }})

        # place Judge - this should be handled by the JSON response though... 
        req_to_send.append({
            'replaceAllText': {
                'containsText': {'text': '{{judge}}'},
                'replaceText': judge_names[judge],
                'pageObjectIds': [ page_id ]
        }})


    # Create the requests to empty placeholders that we didn't use
    for slide_id in new_slide_ids:
        for element in elements_to_slide_index[slide_id]:
            placeholder = '{{%s}}'% element
            req_to_send.append({
             'replaceAllText': {
                 'containsText': {'text': placeholder },
                 'replaceText': '',
                 'pageObjectIds': [ slide_id ]
            }})

    #pprint(req_to_send)
    body = {
    'requests': req_to_send
    }
#    response = slides_service.presentations().batchUpdate(presentationId=PRESENTATION_ID,
#        body=body).execute()
#    create_slide_response = response.get('replies')[0].get('duplicateObject')
#    print('Created slide with ID: {%s}'% create_slide_response.get('objectId'))

#
# WORK ON THE MAIN GREETER (MAIN DIGITAL SIGNAGE)
# This is an easy to follow navigation page basically
#
    welcome_by_courtroom = {}
    for judge in welcome:
        for epoch in welcome[judge]:
            #print('%s (Courtroom: %s) [%s]'% (judge,judge_courtrooms[judge],epoch))
            # Need to limit the scope of the welcome information to only show names from the last 15 minutes or so
            # to names in the curent hour maybe - iron this one out later - will help reduce the amount of names shown.
            # For now just add everyone - sort this out later - LOL
            if epoch > right_now_epoch:
                welcome_by_courtroom.setdefault(judge_courtrooms[judge],[]).extend(sorted(set(welcome[judge][epoch])))
#                        pprint(sorted(set(welcome[judge][epoch])))

    #for cr in welcome_by_courtroom:
        #print(cr)
        #pprint(sorted(set(welcome_by_courtroom[cr])))

    update_greeter_svg(welcome_by_courtroom)
# Now we have a SVG file updated with names pointing to courtroom for the main greeter board

print('DONE')

