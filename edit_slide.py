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

print ('** Editing Slide **')
print('** Get slide objects, search for image placeholder')
slide = slides_service.presentations().get(presentationId=PRESENTATION_ID,
	fields='slides').execute().get('slides')[0]
obj = None
for obj in slide['pageElements']:
    if obj['shape']['shapeType'] == 'RECTANGLE':
        break

print('** Searching for icon file')
rsp = drive_service.files().list(q="name='%s'" % IMG_FILE).execute().get('files')[0]
print(' - Found image [%s|%s]' % (rsp['name'], rsp['id']))
img_url = '%s&access_token=%s' % (
        drive_service.files().get_media(fileId=rsp['id']).uri, creds.access_token)

print('** Replacing placeholder text and icon')
reqs = [
    {'replaceAllText': {
        'containsText': {'text': '{{title}}'},
        'replaceText': 'Hello World!'
    }},
    {'createImage': {
        'url': img_url,
        'elementProperties': {
            'pageObjectId': slide['objectId'],
            'size': obj['size'],
            'transform': obj['transform'],
        }
    }},
    {'deleteObject': {'objectId': obj['objectId']}},
]
#slides_service.presentations().batchUpdate(body={'requests': reqs},
#	presentationId=PRESENTATION_ID).execute()

print('DONE')
