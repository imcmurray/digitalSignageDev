#!/usr/bin/env python

from __future__ import print_function
import json,requests,time,gspread
from datetime import date
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

todays_hearings_to_be_heard = {}
judge_inits = ['rkm','wtt','jtm']
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_'

today = date.today()
#formatted_today = today.strftime("%Y-%m-%d")
formatted_today = "2018-05-23"
right_now_epoch = int(time.time())

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
    gc = gspread.authorize(creds)

    SPREADSHEET_ID = '1Jlnn50Ljr4uTqMuwXL8WTuFyC-rqkbWUowmitVFXIXs'
    she = gc.open_by_key(SPREADSHEET_ID)

    # Now we have active hearings and google connections, update the spreadsheet with data
    for judge, v in todays_hearings_to_be_heard.items():
	print(judge)
	worksheet = she.worksheet(judge)
	for k, v in sorted(todays_hearings_to_be_heard[judge].items(),reverse=True):
	    block_time = str(time.strftime('%I:%M %p', time.localtime(k))).lstrip('0')
	    print("\t%s" % block_time)
	    for k1, v1 in v.items():
                row_id = k1+1
		jonj = json.loads(v1)
		print("\t%s = [%s|%s|%s|%s]\n\t%s (%s|%s)\n" % (
			k1, jonj['cs_case_number'], jonj['cs_chapter'], jonj['judge_name'],
			jonj['cs_short_title'], jonj['chs_matter'], jonj['movant_name'],
			jonj['location']
		))
		send = []
                send.append(block_time)
                send.append(jonj['cs_case_number'])
                send.append(jonj['cs_chapter'])
                send.append(jonj['cs_short_title'])
                send.append(jonj['chs_matter'])
                send.append(jonj['movant_name'])
                send.append(jonj['location'])
                worksheet.insert_row(send, row_id)


