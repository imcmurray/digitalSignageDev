#!/usr/bin/env python
"""
Shows basic usage of the Slides API. Prints the number of slides and elments in
a presentation.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from datetime import date
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

# We need to look at the master spreadsheet for entries which do no have a linked file_id to their configuration sheet

# This is the template for new courts
NEW_CONF_SPREADSHEET_ID = '1zRG6Uex-msDs5Av3W9Swzfl-gu1pZnWoHG1VOw0jbMU'

# This is the master spreadsheet that will contain ALL courts configured and their associated configuration file id
MASTER_SPREADSHEET_ID = '1FtGo3rku0DJZvqytetq0y-R-tUQyFdERfSiyhA_SnXw'

# gspread way of life
she = gc.open_by_key(MASTER_SPREADSHEET_ID)
wks = she.worksheet('Bankruptcy')
cll_list = wks.range('B3:E10')
courts = {}
court = ''
courtsToSetup = []
print('Showing configurations:')
for cell in cll_list:
   
    if cell.col == 2:
        if cell.value != '':
            print('\tCourt [%s]'%cell.value)
            courts.setdefault(cell.value,{})
            court = cell.value
        else:
            court = ''

    if court:
        if cell.col == 3:
            if cell.value:
                courts[court]['contact'] = cell.value

        if cell.col == 4:
            if cell.value:
                courts[court]['courtInfo'] = cell.value

        if cell.col == 5:
            if cell.value:
                courts[court].setdefault('configFile', { 'fileId': cell.value, 'coords': {'row': '', 'col': ''}})
            else:
                coords = { 'fileId': '', 'row': cell.row, 'col': cell.col }
                courts[court].setdefault('configFile', {}).setdefault('coords', {})
                courts[court]['configFile']['coords'] = coords
                courtsToSetup.append(court)

#print(courts)
#exit()
if len(courtsToSetup):

    print('Processing any missing configurations:')

    today = date.today()
    formatted_today = today.strftime("%Y-%m-%d")

    vWorksheet = she.worksheet('VARIABLES')
    templateFileId = vWorksheet.acell('C3').value
    print('Found template file id [%s]'%templateFileId)

    for court in courtsToSetup:
        print('\tSetting up [%s]'%court)

        body = {
            'name': 'FRESH %s DS Configuration'% court
        }
        #drive_response = drive_service.files().copy(fileId=MASTER_SPREADSHEET_ID, body=body).execute()
        drive_response = drive_service.files().copy(fileId=NEW_CONF_SPREADSHEET_ID, body=body).execute()
        configFileId = drive_response.get('id')

        # The idea was to parse the CourtInfo location for each court
        # and automatically create configuration based on the XML...
        # But I think it would be best to just copy the config file
        # and manually walk through it - June 2018

        # Not sure why we are setting this here - no use!
        courts[court]['configFile']['name'] = configFileId

        # update master with new File ID for this court
        wks.update_cell(courts[court]['configFile']['coords']['row'],
                courts[court]['configFile']['coords']['col'], configFileId)

        # update master with the date we performed the setup
        wks.update_cell(courts[court]['configFile']['coords']['row'],
                courts[court]['configFile']['coords']['col']+1, formatted_today)

        print('\t\tDONE')

else:
    print('No setup action required!')



---

#Python code to illustrate parsing of XML files
# importing the required modules
import csv
import json
import requests
import xml.etree.ElementTree as ET

# creating HTTP response object from given url
courtInfoUrl = 'https://ecf.utb.uscourts.gov/cgi-bin/CourtInfo.pl?output=xml&location=main'
#courtInfoUrl = 'https://ecf.wawb.uscourts.gov/cgi-bin/CourtInfo.pl?output=xml&location=main'
resp = requests.get(courtInfoUrl)
tree = ET.ElementTree(ET.fromstring(resp.content))
#print(tree)
root = tree.getroot()
#print(root)

#def show(elem):
#    print elem.tag
#    for child in elem.findall('*'):
#        show(child)

def show(elem, indent = 0):
    #print ' ' * indent + elem.tag
    for child in elem.findall('*'):
        show(child, indent + 1)

show(root)

courtInfo={}
#print root.find('CourtName').text
#print root.find('Locations/website').text
cmecfRelease = root.find('ReleaseID').text
#for e in root.findall('Locations/name'):
#courtInfo['courtName'] = root.find('CourtName').text
courtName = root.find('CourtName').text
print('US Bankruptcy Court, %s'% courtName)
cmecfRelease = root.find('ReleaseID').text
print(cmecfRelease)
locationCount=0
locationInfo={}
locations=[]
for e in root.findall('Locations/*'):
    if 'name' in e.tag:
        print('Location [%s]'%(locationCount+1))
        locationCount+=1
    print('\t[%s] = %s'% (e.tag, e.text))

# JSON extraction
#url = 'https://www.utb.uscourts.gov/chamberaccess/active_hearings_rkm.json'
#response = requests.get(url)
#json_obj = response.json()

#for k in range(len(json_obj['rows'])):

#tree = ET.parse(resp)

--=
