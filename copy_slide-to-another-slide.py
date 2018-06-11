"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
import json,requests,time
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint

# Setup the Slides API
IMG_FILE = 'google-slides.png'     # use your own!
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
#drive_service = build('drive', 'v3', http=creds.authorize(Http()))

# Call the Slides API
PRESENTATION_ID = '1CuDcEYKxvJGF1dWQrjnhW3GrPWB6bQxe0cTauKRXWa4'
pageId_template = 'template-table-hearings-slide'

print ('** Copying slide **')
#pageId_template = 'template-table-hearings-slide'
pageId_copy = 'copiedSlide4'
requests = [
  {
    "duplicateObject": {
      "objectId": pageId_template,
      "objectIds": {
          "template-table-hearings-slide": pageId_copy
      }
    }
  }
]

# Slide is copied and waiting for us to do something with it!

# Can we do the replacement too?
requests.append({
    'replaceAllText': {
        'containsText': {'text': '{{elem-htime-1}}'},
        'replaceText': 'Hello World!',
        'pageObjectIds': [ pageId_copy ]
}})

# place timestamp
requests.append({
    'replaceAllText': {
        'containsText': {'text': '{{last-updated}}'},
        'replaceText': str(time.strftime('%c', time.localtime())),
        'pageObjectIds': [ pageId_copy ]
}})

# place courtroom
requests.append({
    'replaceAllText': {
        'containsText': {'text': '{{courtroom}}'},
        'replaceText': 'COMING SOON!',
        'pageObjectIds': [ pageId_copy ]
}})

# place Hearing Date
requests.append({
    'replaceAllText': {
        'containsText': {'text': '{{hearing-date}}'},
        'replaceText': 'Wednesday May 23rd 2018',
        'pageObjectIds': [ pageId_copy ]
}})

# place Judge - this should be handled by the JSON response though... 
requests.append({
    'replaceAllText': {
        'containsText': {'text': '{{judge}}'},
        'replaceText': 'COMING SOON!',
        'pageObjectIds': [ pageId_copy ]
}})

# Cycle through the elements - should we see how many we have first?
# so we know how many need to have their text replaced



body = {
	'requests': requests
}
response = slides_service.presentations().batchUpdate(presentationId=PRESENTATION_ID,
body=body).execute()
create_slide_response = response.get('replies')[0].get('duplicateObject')
print('Created slide with ID: {%s}'% create_slide_response.get('objectId'))
print('Done')



