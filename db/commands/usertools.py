# -*- coding: utf-8 -*-
from flask import current_app
from commands import comptes 

import requests

proxies = {
        'http': 'http://135.245.192.7:8000',
        'https': 'http://135.245.192.7:8000',
        }

@comptes.command
def list ():
    u"liste des comptes"
    pass
