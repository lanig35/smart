#!/usr/bin/env python

import requests
import json

url = 'https://www.googleapis.com/books/v1/volumes/'
proxies = {
    'http': 'http://135.245.192.7:8000',
    'https': 'http://135.245.192.7:8000'
}
params = {
    'langRestrict': 'fr',
    'projection': 'lite',
    'key': 'AIzaSyC8kptWtpdhgNWcdHItIscjlpJAMFtI17U',
    'fields': 'totalItems,items(selfLink)',
    'q': 'intitle:route+inauthor:london'
}

r = requests.get (url, proxies=proxies, params=params)

if r.status_code != 200:
    print r.text
    exit (1)

data = r.json()

if data['totalItems'] != 1:
    exit (1)

params = {
    'key': 'AIzaSyC8kptWtpdhgNWcdHItIscjlpJAMFtI17U',
    'fields': 'volumeInfo, saleInfo'
}

r = requests.get (data['items'][0]['selfLink'], proxies=proxies, params=params)

data = r.json()

params = {
    'format': 'json',
    'jcmd': 'data',
    'bibkeys': 'ISBN\:'+data['volumeInfo']['industryIdentifiers'][1]['identifier']
}

r = requests.get ('http://openlibray.org/api/books', proxies=proxies, params=params)
print r.url
if r.status_code != 200:
    print r.text
    exit (1)

print r.text

#print json.dumps (r.json())
