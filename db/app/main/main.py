# -*- coding: utf-8 -*-
from flask import current_app, render_template
import requests

from . import bp_main

@bp_main.route ('/')
def index():
    current_app.logger.info ('request')
    return (render_template ('index.html', title='Home', name='Alain'))

@bp_main.route ('/auteurs')
def auteurs ():
    current_app.logger.info ('request')
    r = requests.get ('http://localhost:5984/alain/_all_docs', params={'limit':5, 'include_docs': True})

    table = []
    for item in r.json()['rows']:
        data = {'nom':item['doc']['nom'],
                'prenom': item['doc']['prenom'],
                'pays': item['doc']['pays']}
        table.append (data)

    return (render_template ('auteurs.html', title='auteurs', auteurs=table))


