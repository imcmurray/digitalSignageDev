#!/usr/bin/env python

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

