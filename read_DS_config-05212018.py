"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
import json,requests,time
from datetime import date
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Slides API
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/spreadsheets',
)
#SCOPES = 'https://www.googleapis.com/auth/presentations.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
slides_service = build('slides', 'v1', http=creds.authorize(Http()))
drive_service = build('drive', 'v3', http=creds.authorize(Http()))
sheets_service = build('sheets', 'v4', http=creds.authorize(Http()))

# Load configuration from config.json
with open('./config.json') as f:
    config = json.load(f)

# Call the Sheets API
SPREADSHEET_ID = config['GOOGLE']['SPREADSHEET']['fileId']

RANGE_NAME = 'endpoints!B5:C'
result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
numRows = result.get('values') if result.get('values')is not None else 0

# Sort out which judge is in which courtroom
courtroom_to_judges={}
judge_to_endpoints={}
for a,b in numRows:
    judges = b.split(',')
    print('Judges:%s'%judges)
    for judge in judges:
        judge_to_endpoints[str(judge)]={ 'courtroom': str(a)}
    courtroom_to_judges[str(a)]=str(b)

print(courtroom_to_judges)
#print(judge_to_endpoints)

# Now we know who will be in which courtroom today...
# - by judge inits (dict:judge_to_endpoints [index:judge inits|value=courtroom number)
# - by courtroom (dict:courtroom_to_judges [index:courtroom number|value=judge inits)
# WARNING: dict:courtroom_to_judges values might contain multiple judge inits, seperated by ','

# Loadup more configuration information 
for judge in judge_to_endpoints:
    RANGE_NAME = '%s!B5:E9' % judge
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    nRows = result.get('values') if result.get('values')is not None else 0
    for v1,v2,v3,v4 in nRows:
        ind = str(v1.replace(" ","_").lower())
        #print('%s | %s | %s | %s'%(ind,str(v2),str(v3),str(v4)))
        judge_to_endpoints[judge][ind]={ 'max_hearings': int(v2), 'slide_id': str(v3), 'presentation_id': str(v4) }
    JUDGE_NAME = '%s!C2:C2' % judge
    jresult = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=JUDGE_NAME).execute()
    jrows = jresult.get('values') if jresult.get('values')is not None else 0
    for jn in jrows:
        judge_to_endpoints[judge]['name']=str(jn[0])

# Just added a whole bunch of data from the judges spreadsheet configuration page to
# dict:judge_to_endpoints [index:judge inits|value=courtroom number+spreadsheet information)

print(judge_to_endpoints)

# Now that we've loaded the configuration, take a look at each judges hearings

todays_hearings_to_be_heard = {}
daily_hearing_totals = {}
judge_day_to_template = {}
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_'

today = date.today()
formatted_today = today.strftime("%Y-%m-%d")
#formatted_today = "2018-05-23"
right_now_epoch = int(time.time())

for judge in judge_to_endpoints:
    print("Working on Judge [%s]" % judge)
    judge_json_url = "%s%s.json" % (url, judge)

    # JSON extraction
    response = requests.get(judge_json_url)
    json_obj = response.json()

    for k in range(len(json_obj['rows'])):
        inday = json_obj['rows'][k]['id']
        event = json_obj['rows'][k]['value']
        daily_hearing_totals.setdefault(judge,{}).setdefault(inday,0)
        daily_hearing_totals[judge][inday]+=1

        #if inday == formatted_today:
        if event['hearing_set'] > right_now_epoch:
            todays_hearings_to_be_heard.setdefault(judge,{}).setdefault(event['hearing_set'],{})[event['sort_count']] = json.dumps(event);

    for judge, v in todays_hearings_to_be_heard.items():
        print(judge)
	for k, v in sorted(todays_hearings_to_be_heard[judge].items(),reverse=True):
	    block_time = str(time.strftime('%Y-%m-%d %I:%M %p', time.localtime(k))).lstrip('0')
	    print("\t%s contains %s hearings" % (block_time,len(v)))

            for el in judge_to_endpoints[judge]:
                if 'hearings' in el:
                    if judge_to_endpoints[judge][el]['max_hearings'] > len(v):
                        print('template description would work: %s since #hrgs %s is under %s'% (el,len(v),judge_to_endpoints[judge][el]['max_hearings']))

	    #for k1, v1 in v.items():
                #row_id = k1+1
		#jonj = json.loads(v1)
		#print("\t%s = [%s|%s|%s|%s]\n\t%s (%s|%s)\n" % (
		#   k1, jonj['cs_case_number'], jonj['cs_chapter'], jonj['judge_name'],
		#   jonj['cs_short_title'], jonj['chs_matter'], jonj['movant_name'],
		#jonj['location']
		#))

template_picker={}
print('daily_hearing_totals:\n%s'% daily_hearing_totals)
for judge in judge_to_endpoints:
    #template_picker[judge]={}
    # How do we determine the smaller template to use....
    for el in judge_to_endpoints[judge]:
        if 'hearings' in el:
            for inday in daily_hearing_totals[judge]:
                if judge_to_endpoints[judge][el]['max_hearings'] > daily_hearing_totals[judge][inday]:
                    #print('Judge: %s on %s use %s{%s} template due to %s hearings'% (judge,
                    #    inday, el, judge_to_endpoints[judge][el]['slide_id'], daily_hearing_totals[judge][inday]))
                    template_picker.setdefault(judge,{}).setdefault(inday,[]).append(judge_to_endpoints[judge][el]['max_hearings'])

for judge in template_picker:
    for inday in template_picker[judge]:
        smallest = min(template_picker[judge][inday])
        print('%s - %s - %s'% (judge, inday, smallest))
        for el in judge_to_endpoints[judge]:
            if 'hearings' in el:
                if judge_to_endpoints[judge][el]['max_hearings'] == smallest:
                    print('\tTemplate slide to use: %s{%s}'% (el, judge_to_endpoints[judge][el]['slide_id']))
                    judge_day_to_template.setdefault(judge,{}).setdefault(str(inday),{})['slide_id'] = judge_to_endpoints[judge][el]['slide_id']
                    judge_day_to_template.setdefault(judge,{}).setdefault(str(inday),{})['presentation_id'] = judge_to_endpoints[judge][el]['presentation_id']
                    judge_day_to_template.setdefault(judge,{}).setdefault(str(inday),{})['template_description'] = el

print(judge_day_to_template)

# Now work on the greeter

RANGE_NAME = 'greeter!B2:G'
result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
numRows = result.get('values') if result.get('values')is not None else 0
print(result.get('values'))



