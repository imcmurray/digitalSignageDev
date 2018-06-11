"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

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
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

# Call the Slides API
PRESENTATION_ID = '1AnsN_4VnuWEo-a7bbRAL-NTys5-XnU3gXuPQJjMedOk'
presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
slides = presentation.get('slides')

print ('The presentation contains {} slides:'.format(len(slides)))
for i, slide in enumerate(slides):
    print('- Slide #{} contains {} elements.'.format(i + 1,
                                                     len(slide.get('pageElements'))))

print ('** Copying slide **')
body = {
    'name': 'This is a COPY'
}



drive_response = drive_service.files().copy(fileId=PRESENTATION_ID, body=body).execute()
presentation_copy_id = drive_response.get('id')
print ('presentation id of the copy: %s' % presentation_copy_id)

