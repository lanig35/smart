# -*- coding: utf-8 -*-
from flask import current_app
from commands import tickets

import requests

proxies = {
        'http': 'http://135.245.192.7:8000',
        'https': 'http://135.245.192.7:8000',
        }

@tickets.command
def list ():
    "liste des tickets"
    r = requests.get ('https://api.github.com/repos/lanig35/smart/issues', proxies=proxies)
    print r.json()
