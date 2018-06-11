"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
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

# Call the Sheets API
SPREADSHEET_ID = '1CoIS_AjwBhs009edRuFCyMV-yymWNzO99sVK2kl-t3w'
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


