"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import gspread

# Setup the Slides API
IMG_FILE = 'google-slides.png'     # use your own!
TMPLFILE = 'title slide template'  # use your own!
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
gc = gspread.authorize(creds)

# Call the Slides API
PRESENTATION_ID = '1XRz6VXLyr49iv008hON8ZCvuM0OnUZ9QeZcaFXYhM4w'
presentation = slides_service.presentations().get(presentationId=PRESENTATION_ID).execute()
slides = presentation.get('slides')

print ('The presentation contains {} slides:'.format(len(slides)))
for i, slide in enumerate(slides):
    print('- Slide #{} contains {} elements.'.format(i + 1,
                                                     len(slide.get('pageElements'))))

#print ('** Copying slide **')
#body = {
#    'name': 'This is a COPY'
#}
#drive_response = drive_service.files().copy(fileId=PRESENTATION_ID, body=body).execute()
#presentation_copy_id = drive_response.get('id')
#print ('presentation id of the copy: %s' % presentation_copy_id)

#title = 'Hello Ian'
#body = {
#    'title': title
#}
#new_presentation = slides_service.presentations().create(body=body).execute()
#print('Created presentation with ID: {0}'.format(new_presentation.get('presentationId')))

# Call the Sheets API
SPREADSHEET_ID = '1Jlnn50Ljr4uTqMuwXL8WTuFyC-rqkbWUowmitVFXIXs'
RANGE_NAME = 'Test!A2:E'
result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
numRows = result.get('values') if result.get('values')is not None else 0
print('{0} rows retrieved.'.format(numRows))

#print('** Writing to sheets')
#RANGE_NAME = 'Test!A6:E'
#values = [
#    [
#	'This is A6','This is B6', 'This is C6', 'This is D6'
#    ],
#    [
#	'This is A7','This is B7', 'This is C7', 'This is D7'
#    ],
#]
#body = {
#    'values': values
#}
#value_input_option = 'RAW'
#result = sheets_service.spreadsheets().values().update(
#    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
#    valueInputOption=value_input_option, body=body).execute()
#print('{0} cells updated.'.format(result.get('updatedCells')));


# gspread way of life
she = gc.open_by_key(SPREADSHEET_ID)
wks = she.worksheet('Test')
cll_list = wks.range('A1:B8')
print(cll_list)
print('** Update a cell')
wks.update_acell('A1', 'Hello Ian!')

# Select a range
cell_list = wks.range('A10:C12')

for cell in cell_list:
    cell.value = '%s-%s'%(cell.row,cell.col)

# Update in batch
wks.update_cells(cell_list)

presentation_id_2_update = '1CuDcEYKxvJGF1dWQrjnhW3GrPWB6bQxe0cTauKRXWa4'

#RANGE_NAME = 'Class Data!A2:E'
#result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
#                                             range=RANGE_NAME).execute()
#values = result.get('values', [])
#if not values:
#    print('No data found.')
#else:
#    print('Name, Major:')
#    for row in values:
        # Print columns A and E, which correspond to indices 0 and 4.
#        print('%s, %s' % (row[0], row[4]))
