#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import Tkinter as tk
import requests
import json

print (sys.argv)

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
url = 'http://localhost:5984/alain/_design/authors/_view/parNom'
params = {
    'key': '\"{}\"'.format (sys.argv[1].title()),
    'include_docs': True
}
print params
r = requests.get (url, headers=headers, params=params)
print url

if r.status_code != 200:
    print r.text
    exit (1)

print r.json()

w = tk.Tk ()
w.title (r.json()['rows'][0]['doc']['nom'])
n = tk.Label (w, text=r.json()['rows'][0]['doc']['nom'])
p = tk.Label (w, text=r.json()['rows'][0]['doc']['prenom'])
l = tk.Label (w, text=r.json()['rows'][0]['doc']['langue'])
b = tk.Button (w, text='fermer')

p.grid (column=2, row=1)
n.grid (column=6, row=1)
l.grid (column=2, row=2)
b.grid (column=4, row=5)

w.mainloop ()
