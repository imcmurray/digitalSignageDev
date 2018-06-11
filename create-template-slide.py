#!/usr/bin/env python

from __future__ import print_function
import json,requests,time,random
from datetime import date
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint

# Setup OAUTH2 scope and connection to Google
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
presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
# We're just going to create the page - maybe?
#slides = presentation.get('slides')

# setup some other variables
element_columns = ['htime','cnum','ctitle', 'hmatter', 'hmovant']
element_column_widths = {'htime': 100, 'cnum': 100, 'ctitle': 100, 'hmatter':
        300, 'hmovant': 100}
pos = { 'x': 20, 'y': 20, 'row': 1, 'col': 1, 'standard_height': 14,
        'standard_font_size': 8, 'max_bottom': 371, 'starting_x': 20,
        'starting_y': 20}
insert_on_page=1
today = date.today()
formatted_today = today.strftime("%h%m%s")

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
pt20 = {
        'magnitude': 20,
        'unit': 'PT'
        }
pt15 = {
        'magnitude': 15,
        'unit': 'PT'
        }

req_to_send = []

# Create the slide
slide_id = 'template-table-hearings-slide'
print('** creating a new slide id [%s]'% slide_id)
req_to_send.append({
    'createSlide': {
        'objectId': slide_id,
        'insertionIndex': insert_on_page,
        'slideLayoutReference': {
            'predefinedLayout': 'BLANK'
            }
        }
    })

for elem in element_columns:
    print('Working on element [%s]'% elem)
    pos['row'] = 1
    pos['y'] = pos['starting_y']
    while ( pos['y'] < pos['max_bottom'] ):
        element_id = 'elem-%s-%s' % (elem, pos['row'])
        print('\tWorking on element [%s]' % element_id)

        ptwidth = 'pt%s'% str(element_column_widths[elem])

        req_to_send.append({
            'createShape': {
                'objectId': element_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': pt20,
                        'width': eval(ptwidth),
                        },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': pos['x'],
                        'translateY': pos['y'],
                        'unit': 'PT'
                        }
                    }
                }
            })

        template_text = '{{%s}}'% element_id
        # Insert text into the box, using the supplied element ID.
        req_to_send.append({
            'insertText': {
                'objectId': element_id,
                'insertionIndex': 0,
                'text': template_text
                }
            })

        #Update the formatting of the text
        req_to_send.append({
            'updateTextStyle': {
                'objectId': element_id,
                'style': {
                    'fontFamily': 'Roboto',
                    'fontSize': {
                        'magnitude': pos['standard_font_size'],
                        'unit': 'PT'
                        },
                    'foregroundColor': {
                        'opaqueColor': {
                            'rgbColor': {
                                'blue': 1.0,
                                'green': 1.0,
                                'red': 1.0
                                }
                            }
                        }
                    },
                'fields': 'foregroundColor,fontFamily,fontSize'
                } 
            })
        # get ready for next run
        pos['y'] = pos['y'] + pos['standard_height']
        pos['row'] = pos['row'] + 1

    pos['x'] = pos['x'] + element_column_widths[elem]

#pprint(req_to_send)
body = {
    'requests': req_to_send
}
response = slides_service.presentations().batchUpdate(presentationId=PRESENTATION_ID,
    body=body).execute()
create_slide_response = response.get('replies')[0].get('createSlide')
print('Created slide with ID: {0}'.format(create_slide_response.get('objectId')))

print('DONE')
