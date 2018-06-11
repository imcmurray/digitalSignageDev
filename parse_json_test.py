#!/usr/bin/env python

import json,requests,time,collections
from datetime import date
from pprint import pprint

today = date.today()
formatted_today = today.strftime("%Y-%m-%d")
right_now_epoch = int(time.time())
print "%s" % formatted_today
print "Epoch: %s" % right_now_epoch
print "Time now: %s" % time.localtime()

url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_rkm.json'
response = requests.get(url)

# Convert bytes to string type and string type to dict
json_obj = response.json()
#pprint(json_obj)
#print('%s' % json_obj)

process_days_index = {}
#todays_hearings_to_be_heard = []
todays_hearings_to_be_heard = {}

for d in json_obj['rows']:
    print d['value']['sort_count']
    #print 'Day: %s' % d['id']
    #process_days.append(d['id'])
    inday = d['id']
    if inday == formatted_today:
        # Change the less than to a greater than - less just for testing due to time st developing
        if d['value']['hearing_set'] > right_now_epoch:
            ts = str(time.strftime('%I:%M %p', time.localtime(d['value']['hearing_set']))).lstrip('0')

            print "Epoch for case# %s (%s|%s) = %s or %s" % (d['value']['cs_case_number'], d['value']['sort_order'],d['value']['sort_count'],d['value']['hearing_set'],ts)
            #print "Time localtime: %s" % time.localtime(d['value']['hearing_set'])
            #todays_hearings_to_be_heard.insert(d['value']['sort_count'],d['value'])
            print "Sort Count: %s" % d['value']['sort_count']
            todays_hearings_to_be_heard.setdefault(d['value']['hearing_set'],[]).insert(d['value']['sort_count'],d['value'])

    #if not inday in process_days_index:
        #process_days_index[inday]=1;
    #else:
        #process_days_index[inday]+=1;

#print '%s' % todays_hearings_to_be_heard
#print('%s' % process_days_index)


#pprint(todays_hearings_to_be_heard)

for k, v in todays_hearings_to_be_heard.items():
    print k
    for hcount in range(len(todays_hearings_to_be_heard[k])):
    #for val in todays_hearings_to_be_heard[k]:
        print '%s = %s' % (hcount, todays_hearings_to_be_heard[k][hcount]['sort_count'])



#pprint(process_days_index)
#print(json_obj['source_name']) # prints the string with 'source_name' key
