#!/usr/bin/env python

from __future__ import print_function
import json,requests,time,random,re
from subprocess import call
from datetime import date
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from HTMLParser import HTMLParser

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
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

folder_id = '1lxacudR6cZwBqJGMYpEENwOQDI6y8MMe'
    #file_metadata = {
    #            'name': 'quick-case-map.png',
    #                'parents': [folder_id]
    #                }
    #media = MediaFileUpload('quick-case-map.png',
    #    mimetype='image/png',
    #    resumable=True)
    #file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    #print('File ID: %s' % file.get('id'))

    # File's new metadata.
    #$file->setTitle('file.xls');
    #$file->setFileSize(filesize('file.xls'));

    # File's new content.
#    file_metadata = {
#                'name': 'quick-case-map.png',
#                    'parents': [folder_id]
#                    }
#media = MediaFileUpload('welcome-template.png',

media = MediaFileUpload('quick-case-map.png',
    mimetype='image/png',
    resumable=True)
file_id = '1-XncbSa_I_PxKqGAtZZ-Q6x4BVDcDFUe'
file = drive_service.files().update(fileId=file_id, media_body=media, keepRevisionsForver=False, fields="id").execute()


 
# Now we have a SVG file updated with names pointing to courtroom for the main greeter board

print('DONE')

