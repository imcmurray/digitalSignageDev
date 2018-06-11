#!/usr/bin/env python

from __future__ import print_function
import json,requests,time,gspread,random
from datetime import date
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from HTMLParser import HTMLParser

todays_hearings_to_be_heard = {}
judge_inits = ['rkm','wtt','jtm']
url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_'
h = HTMLParser()

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
    #gc = gspread.authorize(creds)

    PRESENTATION_ID = '1CuDcEYKxvJGF1dWQrjnhW3GrPWB6bQxe0cTauKRXWa4'
    presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
    #slides = presentation.get('slides')
    #she = gc.open_by_key(SPREADSHEET_ID)

    pt700 = {
        'magnitude': 700,
        'unit': 'PT'
    }
    pt500 = {
        'magnitude': 500,
        'unit': 'PT'
    }
    pt350 = {
        'magnitude': 350,
        'unit': 'PT'
    }
    pt300 = {
        'magnitude': 300,
        'unit': 'PT'
    }
    pt200 = {
        'magnitude': 200,
        'unit': 'PT'
    }
    pt150 = {
        'magnitude': 150,
        'unit': 'PT'
    }
    pt100 = {
        'magnitude': 100,
        'unit': 'PT'
    }
    pt50 = {
        'magnitude': 50,
        'unit': 'PT'
    }
    pt30 = {
        'magnitude': 30,
        'unit': 'PT'
    }

    req_to_send = []

    start_insert_on_page=1
    # Now we have active hearings and google connections, update the spreadsheet with data
    for judge, v in todays_hearings_to_be_heard.items():
	print(judge)
        #page_id = '%sslideb0' % judge
        #req_to_send.append({
        #    'createSlide': {
        #        'objectId': page_id,
        #        'insertionIndex': '1',
        #        'slideLayoutReference': {
        #            'predefinedLayout': 'BLANK'
        #        }
        #    }
        #})
	#worksheet = she.worksheet(judge)
	#for k, v in sorted(todays_hearings_to_be_heard[judge].items(),reverse=True):
	for k, v in sorted(todays_hearings_to_be_heard[judge].items()):
	    block_time = str(time.strftime('%I:%M %p', time.localtime(k))).lstrip('0')
            page_id = '%sslide%sd0' % (judge, str(time.strftime('%I%M%p', time.localtime(k))))
            req_to_send.append({
                'createSlide': {
                    'objectId': page_id,
                    'insertionIndex': start_insert_on_page,
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            })

            title_element_id = '%stitle%s'% (page_id, str(time.strftime('%I%M%p', time.localtime(k))))
            # Create page title text box and position it
            req_to_send.append({
                'createShape': {
                'objectId': title_element_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': pt50,
                    'width': pt700
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': 20,
                    'translateY': 20,
                    'unit': 'PT'
                }
                }
                }
            })

            # Insert text into the box, using the supplied element ID.
            req_to_send.append({
                'insertText': {
                    'objectId': title_element_id,
                    'insertionIndex': 0,
                    'text': 'Courtroom 12n - Judge %s on %s' % (judge, str(time.strftime('%c', time.localtime(k))))
                }
            })

            #Update the formatting of the text
            req_to_send.append({
                'updateTextStyle': {
                    'objectId': title_element_id,
                    'style': {
                        'fontFamily': 'Roboto',
                        'fontSize': {
                            'magnitude': 12,
                            'unit': 'PT'
                        },
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {
                                    'blue': 0.0,
                                    'green': 0.0,
                                    'red': 0.0
                                }
                            }
                        }
                    },
                    'fields': 'foregroundColor,fontFamily,fontSize'
                } 
            })


            start_insert_on_page=start_insert_on_page+1
            print("\t%s" % block_time)
            posY=20
            posX=20
	    for k1, v1 in v.items():
                row_id = k1+1
                posY = posY+30
                if posY > 330:
                    posY=50
                    if posX == 20:
                        posX = 220
                    elif posX == 220:
                        posX = 420
                    else:
                        posX = 620

                element_id = '%selema%s%s%s' % (judge, str(time.strftime('%I%M%p', time.localtime(k))), int(random.random()*100), row_id)
		jonj = json.loads(v1)
		print("\t%s (%s|%s) = [%s|%s|%s|%s]\n\t%s (%s|%s)\n" % (
			k1, page_id, element_id, jonj['cs_case_number'], jonj['cs_chapter'], jonj['judge_name'],
			jonj['cs_short_title'], jonj['chs_matter'], jonj['movant_name'],
			jonj['location']
		))
                #toSlide = '%s [%s] %s %s\n%s' % (block_time, k1, jonj['cs_case_number'], jonj['cs_short_title'], jonj['chs_matter'])

                # Sort out the cs_short_title
                # We only want the first init, lastname
                smaller_case_title = ''
                case_title_pieces = jonj['cs_short_title'].split(" and ")
                if case_title_pieces:
                    if len(case_title_pieces) >= 3: # more than two people/company! limit on size instead
                        smaller_case_title = (jonj['cs_short_title'][:30] + '...') if len(jonj['cs_short_title']) > 33 else jonj['cs_short_title']
                    elif len(case_title_pieces) == 2:
			p1 = case_title_pieces[0].split(" ")
		        p1_first = p1[0]
		        p2 = case_title_pieces[1].split(" ")
		        p2_first = p2[0]
		        smaller_case_title = '%s. %s & %s. %s'% (p1_first[0], p1[-1], p2_first[0], p2[-1])
                    else:
                        if ',' in case_title_pieces[0]:
                            smaller_case_title = (jonj['cs_short_title'][:30] + '...') if len(jonj['cs_short_title']) > 33 else jonj['cs_short_title']
                        else:
     			    p1 = case_title_pieces[0].split(" ")
		            p1_first = p1[0]
		            smaller_case_title = '%s. %s'% (p1_first[0], p1[-1])

                smaller_matter = (jonj['chs_matter'][:130] + '...') if len(jonj['chs_matter']) > 133 else jonj['chs_matter']
                toSlide = '%s  %s\n%s' % (jonj['cs_case_number'], h.unescape(smaller_case_title), h.unescape(smaller_matter))

                # Create text box and position it (combining all data points for POC)
                req_to_send.append({
                    'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': pt50,
                        'width': pt200
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': posX,
                        'translateY': posY,
                        'unit': 'PT'
                    }
                    }
                    }
                })

                # Insert text into the box, using the supplied element ID.
                req_to_send.append({
                    'insertText': {
                        'objectId': element_id,
                        'insertionIndex': 0,
                        'text': toSlide
                    }
                })

                #Update the formatting of the text (Just the font size and color here)
                req_to_send.append({
                    'updateTextStyle': {
                        'objectId': element_id,
                        'style': {
                            'fontFamily': 'Roboto',
                            'fontSize': {
                                'magnitude': 8,
                                'unit': 'PT'
                            },
                            'foregroundColor': {
                                'opaqueColor': {
                                    'rgbColor': {
                                        'blue': 1.0,
                                        'green': 0.0,
                                        'red': 0.0
                                    }
                                }
                            }
                        },
                        'fields': 'foregroundColor,fontFamily,fontSize'
                    } 
                })

                # Make the case number bold and a little larger
                req_to_send.append({
                    'updateTextStyle': {
                        'objectId': element_id,
                        'textRange': {
                            'type': 'FIXED_RANGE',
                            'startIndex': 0,
                            'endIndex': 8
                        },
                        'style': {
                            'bold': True,
                            'fontSize': {
                                'magnitude': 9,
                                'unit': 'PT'
                            },
                       },
                        'fields': 'bold,fontSize'
                    } 
                })

                # Make the case title gray
                req_to_send.append({
                    'updateTextStyle': {
                        'objectId': element_id,
                        'textRange': {
                            'type': 'FIXED_RANGE',
                            'startIndex': 8,
                            'endIndex': toSlide.find('\n')
                        },
                        'style': {
                            'italic': True,
                            'foregroundColor': {
                                'opaqueColor': {
                                    'rgbColor': {
                                        'blue': 0.0,
                                        'green': 0.0,
                                        'red': 0.0
                                    }
                                }
                            }
                        },
                        'fields': 'italic,foregroundColor'
                    } 
                })


                # Add some extra space for larger matters
                if len(smaller_matter) > 55:
                    posY=posY+10
                if len(smaller_matter) > 110:
                    posY=posY+10
                if len(smaller_matter) > 120:
                    posY=posY+5

    #pprint(req_to_send)
    body = {
    'requests': req_to_send
    }
    response = slides_service.presentations().batchUpdate(presentationId=PRESENTATION_ID,
        body=body).execute()
    create_slide_response = response.get('replies')[0].get('createSlide')
    print('Created slide with ID: {0}'.format(create_slide_response.get('objectId')))


print('DONE')
