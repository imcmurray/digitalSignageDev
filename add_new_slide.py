"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Slides API
IMG_FILE = 'leaves-fallen-leaves-HD-Wallpapers.jpg'     # use your own!
TMPLFILE = 'title slide template'  # use your own!
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations',
)
#SCOPES = 'https://www.googleapis.com/auth/presentations.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
slides_service = build('slides', 'v1', http=creds.authorize(Http()))
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

# Call the Slides API
PRESENTATION_ID = '1CuDcEYKxvJGF1dWQrjnhW3GrPWB6bQxe0cTauKRXWa4'
presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
slides = presentation.get('slides')

print ('The presentation contains {} slides:'.format(len(slides)))
for i, slide in enumerate(slides):
    print('- Slide #{} contains {} elements.'.format(i + 1,
                                                     len(slide.get('pageElements'))))

print ('** Adding another Slide to the deck **')
page_id = 'iantestingf'
element_id = 'ian1234felem'
pt350 = {
    'magnitude': 350,
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

# Add a slide at index 1 using the predefined 'TITLE_AND_TWO_COLUMNS' layout and
# the ID page_id.
requests = [
    {
        'createSlide': {
            'objectId': page_id,
            'insertionIndex': '1',
            'slideLayoutReference': {
                'predefinedLayout': 'BLANK'
            }
        }
    },
    {
	'createShape': {
            'objectId': element_id,
            'shapeType': 'TEXT_BOX',
            'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': pt50,
                    'width': pt150
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
    },
    # Insert text into the box, using the supplied element ID.
    {
        'insertText': {
            'objectId': element_id,
            'insertionIndex': 0,
            'text': 'Hello World! New Box with Text Inserted!'
        }
    },
    {
        'updateTextStyle': {
            'objectId': element_id,
            'style': {
                'fontFamily': 'Times New Roman',
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
   }
]

# If you wish to populate the slide with elements, add element create requests here,
# using the page_id.

# Execute the request.
body = {
    'requests': requests
}
response = slides_service.presentations().batchUpdate(presentationId=PRESENTATION_ID,
                                                      body=body).execute()
create_slide_response = response.get('replies')[0].get('createSlide')
print('Created slide with ID: {0}'.format(create_slide_response.get('objectId')))

print('DONE')
