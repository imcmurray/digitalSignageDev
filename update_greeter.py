#!/usr/bin/env python

# This will be the new process (june 11th 2018) of interfacing with the configuration options
# from the spreadsheet entirely. No hard coded values will be used in this code.

from __future__ import print_function
import json,requests,time,random,re,os.path
from subprocess import call, check_output
from datetime import date
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
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
judge_courtrooms = {'rkm': '369', 'wtt': '376', 'kra': '376', 'jtm': '341' }
judge_names = {'rkm': 'Chief Judge R. Kimball Mosier', 'wtt': 'Judge William T. Thurman',
        'jtm': 'Judge Joel T. Marker', 'kra': 'Judge Kevin R. Anderson'}
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_'
template_element_groups = ['elem-htime-','elem-cnum-', 'elem-ctitle-','elem-hmatter-','elem-hmovant-']

h = HTMLParser()
today = date.today()
formatted_today = today.strftime("%Y-%m-%d")
#formatted_today = "2018-05-23"
right_now_epoch = int(time.time())


def get_judges():
    # dict of the judges
    return judges

def get_courtrooms():
    # dict of the courtrooms 
    return courtrooms

def get_templates():
    # dict of templates
    #   including file id of svg location
    return templates

# WORK TO DO IAN TUESDAY JUNE 12th 2018
###

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


def update_greeter_svg(data,epochs_displayed):

    cr_col_pos_index = {}
    for cr in data:
        col = 1
        pos = 1
        #sorted_hearings_per_cr = sorted(set(data[cr]))
        sorted_hearings_per_cr = prepare_name_list(data[cr])
        for name in sorted_hearings_per_cr:
            cr_col_pos = '{{%s-c%s-position%s}}'% (cr, col, pos)
            cr_col_pos_index.setdefault(cr_col_pos,name)
            pos=pos+1
            if pos > 22:
                col = col+1
                pos = 1

    # Prepare time range from epochs_displayed dict
    epoch_range = { 'min': 0, 'max': 0 }
    for epoch in sorted(epochs_use_counter.iterkeys()):
        if epoch_range['min'] == 0:
            epoch_range['min'] = epoch
        epoch_range['max'] = epoch
        print('k[%s] = [%s]'%(epoch,epochs_use_counter[epoch]))
    pprint(epoch_range)
    #exit()

    #pprint(cr_col_pos_index)
    updated = []
    min_time = str(time.strftime('%-I:%M %p', time.localtime(epoch_range['min'])))
    max_time = str(time.strftime('%-I:%M %p', time.localtime(epoch_range['max'])))
    range_time = '%s to %s'%(min_time, max_time)
    if max_time == min_time:
        if epoch_range['min'] == 0 and epoch_range['max'] == 0:
            range_time = ''
        else:
            range_time = 'at %s'%max_time
    now_time = str(time.strftime('%-I:%M %p', time.localtime(right_now_epoch)))
    now_date = today.strftime("%A %B %-d %Y")
    svg_outputfile = 'greeter_%s_%s.svg'%(formatted_today, right_now_epoch)
    print('Would create a new greeter file: %s'% svg_outputfile)
    #with open("welcome-template-05152018-plain.svg") as fin:
    working_on_room = 0
    working_on_room_line_count = 0
    #with open("utb-greeter-template-with-no-events-june052018.svg") as fin:
    with open("utb-greeter-3room-template-06052018.svg") as fin: # SVG Template file
        #with open("updated-greeter-06052018.svg","w") as fout:
        with open(svg_outputfile,"w") as fout:
            for line in fin:
                #line = line.rstrip()
                if working_on_room_line_count:
                    #print('trip: %s = [%s]'%(working_on_room_line_count,line))
                    if re.search(r'display:inline', line) is not None:
                        #print('\tYeah baby we found it!')
                        if working_on_room in data:
                            #print('\tand we are changing the value from! [%s]'%line)
                            line = re.sub(r'display:inline', 'display:none', line)
                            #print('\tand we are changing the value to..! [%s]'%line)
                    working_on_room_line_count-=1

                if re.search(r'id="\d+-no-events"', line) is not None:
                    roomnum = re.findall(r'\d+', line)
                    print('\tFound room number %s'%roomnum)
                    working_on_room = roomnum[0]
                    working_on_room_line_count = 2
                    if roomnum[0] in data:
                        print('\t\tThis room has hearings!')
                        print(data[roomnum[0]])
                    else:
                        print('\t\tThis room has no hearings!')
                if re.search(r'\{\{courtChiefJudge\}\}', line) is not None:
                    line = re.sub(r'\{\{courtChiefJudge\}\}', 'Chief Judge R. Kimball Mosier', line)
                if re.search(r'\{\{courtWeb\}\}', line) is not None:
                    line = re.sub(r'\{\{courtWeb\}\}', 'http://www.utb.uscourts.gov', line)
                if re.search(r'\{\{courtTel\}\}', line) is not None:
                    line = re.sub(r'\{\{courtTel\}\}', 'Tel: 801-524-6687', line)
                if re.search(r'\{\{courtClerk\}\}', line) is not None:
                    line = re.sub(r'\{\{courtClerk\}\}', 'David A. Sime, Clerk of Court', line)
                if re.search(r'\{\{hearing_time\}\}', line) is not None:
                    #line = re.sub(r'\{\{hearing_time\}\}', now_time, line)
                    line = re.sub(r'\{\{hearing_time\}\}', range_time, line)
                if re.search(r'\{\{hearing_date\}\}', line) is not None:
                    line = re.sub(r'\{\{hearing_date\}\}', now_date, line)
                if re.search(r'\{\{\d+-c\d-position\d+\}\}', line) is not None:
                    line = re.sub(r'(\{\{\d+-c\d-position\d+\}\})', lambda m: cr_col_pos_index.get(m.group()), line)
                #updated.append(line)
                fout.write(line)
    return svg_outputfile
    #pprint(updated)



def shorten_case_title(case_title):
    # Sort out the cs_short_title
    # We only want the first init, lastname
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
                smaller_case_title = '%s, %s. &amp; %s.'% (h.unescape(p2[-1]), p1_first[0], p2_first[0])
            else:
                #smaller_case_title = '%s. %s & %s. %s'% (p1_first[0], p1[-1], p2_first[0], p2[-1])
                smaller_case_title = '%s, %s. &amp; %s, %s.'% (h.unescape(p1[-1]), p1_first[0], h.unescape(p2[-1]), p2_first[0])
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
                if re.search(r'.*\bcompany|inc|llc[,.]?$', case_title_pieces[0], flags=re.I): # company found
                    smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
                elif re.search(r'.*\sv.\s.*', case_title_pieces[0], flags=re.I): # Adversary
                    smaller_case_title = (case_title[:30] + '...') if len(case_title) > 33 else case_title
                else:
                    p1 = case_title_pieces[0].split(" ")
                    p1_first = p1[0]
                    #smaller_case_title = '%s. %s'% (p1_first[0], p1[-1])
                    smaller_case_title = '%s, %s.'% (h.unescape(p1[-1]), p1_first[0])

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
            todays_hearings_to_be_heard.setdefault(judge,{}).setdefault(event['hearing_set'],{})[event['sort_count']] = json.dumps(event);

# todays_hearings_to_be_heard contain everything for today
# we need to filter down to 30 minutes either side of the time now

# We also know the epoch time right now
#epoch_now = '%sslide%sd0' % (judge, str(time.strftime('%I%M%p', time.localtime())))

epochs = []
for judge, v in todays_hearings_to_be_heard.items():
    print(judge)
    for k, v in sorted(todays_hearings_to_be_heard[judge].items()):
        block_time = str(time.strftime('%I:%M %p', time.localtime(k))).lstrip('0')
        block_time_diff_to_now_epoch = k-right_now_epoch
        # Positive block_time_diff_to_now_epoch are hearings in the future and vice versa
        print('k=%s - [%s] difference from right now = %s seconds'% (k, block_time, block_time_diff_to_now_epoch))
        if block_time_diff_to_now_epoch < -1800: # 30 minutes is the cut off for blocks to be removed
            print('Removing the above time block! EXPIRED')
            del todays_hearings_to_be_heard[judge][k]
        else:
            epochs.append(k)

#pprint(todays_hearings_to_be_heard)
#exit()
print(epochs)
#
# Need to work out what to do when epochs list is empty... june 6th 2018
#
#print('min epoch: %s and max epoch: %s'%(min(epochs), max(epochs)))
# Now that we have a list of epochs, we need to monitor the range that was
# displayed on the slate so we can show the correct range, rather than everything
# epochs_use_counter dict will be used for this purpose
epochs_use_counter = {}
for v in epochs:
    epochs_use_counter[v] = 0
print(epochs_use_counter)
#exit()

# the epochs list contains a collection of epochs that we would like to display
# so we can use the min and max values to drive the time range we show on the slate

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
                epochs_use_counter[k]+=1

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
# uncomment the following 4 lines if you want to enable the individual courtroom slides to be built
# we are currently skipping because we want to focus on the greeter piece at the moment - June 2018
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
            #print('%s now: %s [min:%s|max:%s]'% (epoch, right_now_epoch, min_epoch, max_epoch))
            welcome_by_courtroom.setdefault(judge_courtrooms[judge],[]).extend(sorted(set(welcome[judge][epoch])))
            #pprint(sorted(set(welcome[judge][epoch])))

    #for cr in welcome_by_courtroom:
        #print(cr)
        #pprint(sorted(set(welcome_by_courtroom[cr])))

    #pprint(welcome_by_courtroom)
    #pprint(epochs_use_counter)
    #for epoch in sorted(epochs_use_counter.iterkeys()):
    #    print('k[%s] = [%s]'%(epoch,epochs_use_counter[epoch]))
    #exit()

    svg_file = update_greeter_svg(welcome_by_courtroom,epochs_use_counter)

    # Perform svg sum comparison with last run? we can skip the update if nothing has changed
    # since we are assuming this is being executed by cron

    old_svg_sum_file = "/tmp/greeter-last-svg-sum.txt"
    new_svg_sum = check_output(["sum", svg_file])
    new_sum = new_svg_sum.split(" ")

    if os.path.isfile(old_svg_sum_file):
        old_svg_sum = check_output(["cat", old_svg_sum_file])
        old_sum = old_svg_sum.split("\n")
        print('old svg sum file found containing: %s'%old_sum[0])

        if new_sum[0] == old_sum[0]:
            print('No changes detected between last run. Exiting')
            os.remove(svg_file)
            exit()
        else:
            # we detected changes so update the old_svg_sum
            print('old sum is different than new sum %s|%s'%(old_sum[0],new_sum[0]))
            with open(old_svg_sum_file, 'w') as f:
                f.write(new_sum[0])
            f.close
            print('updated old svg sum file')
    else:
        # did not find the old svg sum file, so we will create it and continue
        print('Did not find old svg sum file so we will create a new one which contains [%s]'%new_sum[0])
        with open(old_svg_sum_file, 'w') as f:
            f.write(new_sum[0])
        f.close

    # Pass through inkscape so we get a nice PNG output from the SVG
    # inkscape -z -e updated-greeter-05172018.png -w 1920 -h 1080 updated-greeter-05172018.svg
    #call(["inkscape", "-z", "-e", "quick-case-map.png", "-w", "1920", "-h", "1080", svg_file"updated-greeter-06052018.svg"])
    call(["inkscape", "-z", "-e", "quick-case-map.png", "-w", "1920", "-h", "1080", svg_file])

    # Now upload to the greeter location
    # This next folder is owned by utb.ian.mcmurray@gmail.com and is the greeter/live folder for UTB
    folder_id = '1lxacudR6cZwBqJGMYpEENwOQDI6y8MMe'
    #file_metadata = {
    #            'name': 'quick-case-map.png',
    #                'parents': [folder_id]
    #                }
    #media = MediaFileUpload('quick-case-map.png',
    #    mimetype='image/png',
    #    resumable=True)
    #file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    #print('File ID: %s' % file.get('id'))

    # File's new metadata.
    #$file->setTitle('file.xls');
    #$file->setFileSize(filesize('file.xls'));

    # Create a new file new content:
#    file_metadata = {
#                'name': 'quick-case-map.png',
#                    'parents': [folder_id]
#                    }
#    media = MediaFileUpload('quick-case-map.png',
#        mimetype='image/png',
#        resumable=True)
#    file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
#    print('File ID: %s [CREATED]' % file.get('id'))

    # Update an existing file:
    media = MediaFileUpload('quick-case-map.png',
        mimetype='image/png',
        resumable=True)
    file_id = '1-XncbSa_I_PxKqGAtZZ-Q6x4BVDcDFUe'
    file = drive_service.files().update(fileId=file_id, media_body=media, fields="id").execute()
    print('File ID: %s [UPDATED]' % file.get('id'))
 
# Now we have a SVG file updated with names pointing to courtroom for the main greeter board

print('DONE')

