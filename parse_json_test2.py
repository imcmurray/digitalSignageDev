#!/usr/bin/env python

import json,requests,time
from datetime import date

todays_hearings_to_be_heard = {}

today = date.today()
formatted_today = today.strftime("%Y-%m-%d")
right_now_epoch = int(time.time())

# JSON extraction
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_rkm.json'
response = requests.get(url)
json_obj = response.json()

for k in range(len(json_obj['rows'])):
    inday = json_obj['rows'][k]['id']
    event = json_obj['rows'][k]['value']

    if inday == formatted_today:
        if event['hearing_set'] < right_now_epoch:
                todays_hearings_to_be_heard.setdefault(event['hearing_set'],{})[event['sort_count']] = json.dumps(event);

for k, v in todays_hearings_to_be_heard.items():
    block_time = str(time.strftime('%I:%M %p', time.localtime(k))).lstrip('0')
    print block_time
    for k1, v1 in v.items():
        jonj = json.loads(v1)
        print '\t%s = [%s|%s|%s|%s]\n\t%s (%s|%s)\n' % (
                k1, jonj['cs_case_number'], jonj['cs_chapter'], jonj['judge_name'],
                jonj['cs_short_title'], jonj['chs_matter'], jonj['movant_name'],
                jonj['location']

        )

