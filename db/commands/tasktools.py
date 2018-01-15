# -*- coding: utf-8 -*-
from flask import current_app
from commands import taches

import requests, json, uuid, random
from faker import Faker, providers
from slugify import slugify
from prettytable import PrettyTable
import argparse

from util import util

# générateur pseudo-aléatoire de statut
class StatusProvider (providers.BaseProvider):
    def status (self):
        status = [u'new', u'done', u'canceled', u'ongoing']
        return random.choice (status)

@taches.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help='Nombre tâches à créer')
@taches.option (dest='name', metavar='db', nargs='?', help=u'Nom de la base')
def init (count, name=None):
    "création de tâches exemples"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    # création de tâches
    factory = Faker ('fr_FR')
    factory.add_provider (StatusProvider)

    for i in range (0, count):
        title = factory.sentence (nb_words=3)
        payload = {
                "type": "task",
                "title": title,
                "slug": slugify (title),
                "category": factory.word(),
                "priority": factory.word (ext_word_list=('low','medium','high')),
                "status": factory.status(),
                "description": factory.paragraph (nb_sentences=1)
                }

        if not db.put (str(uuid.uuid4()), data=payload):
            return json.dumps (db.status(), indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': count}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@taches.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@taches.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help='Nombre tâches à créer')
@taches.option ('--filter', dest='filter', metavar='filter', default=None, help='Filtrage des tâches')
@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, filter, name=None):
    "liste les tâches"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    # récupération des documents
    params = {
            'limit': count,
            'skip': 0
            }

    if filter == 'prio':
        target = '_design/tasks/_view/byPriority'
        params ['key']='"low"'
        params ['reduce'] = False 
    else:
        target = '_design/tasks/_view/byId'

    view = db.get (target, params)
    if view is None:
        return json.dumps (db.status(), indent=2)

    data = []
    table = PrettyTable (['id', 'title', 'category', 'status', 'priority'])

    for task in view['rows']:
        doc = db.get (task['id'])

        data.append (
                {
                    'id' : doc['_id'],
                    'title': doc['title'],
                    'category': doc['category'],
                    'status': doc['status'],
                    'priority': doc['priority']
                }
            )
        table.add_row([doc['_id'], doc['title'], doc['category'], doc['status'], doc['priority']])

    if f == 'table':
        return table

    sortie = {'total': 10, 'count': 10, 'tasks': data}
    return json.dumps (sortie, indent=2)

@taches.option ('-p', '--prio', dest='prio', choices=['low', 'medium', 'high'], default='medium')
@taches.option ('-c', '--cat', dest='cat', default='default')
@taches.option ('-d', '--db', dest='name', default=None, help=u'Nom de la base')
@taches.option (dest='title', nargs=argparse.REMAINDER, help=u'titre')
def add (prio, cat, name, title):
    "ajout d'une tâche"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    payload = {
            "type": "task",
            "title": ' '.join(title),
            "slug": '-'.join (title),
            "category": cat,
            "priority": prio,
            "status": u'new'
                }

    key = str(uuid.uuid4())
    if not db.put (key, data=payload):
        return json.dumps (db.status(), indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': u'created', 'id': key}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@taches.option ('-i', '--input', dest='data', type=argparse.FileType ('r'), required=True, help='fichier de donneés')
@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def bulk (data, name):
    u'ajout en masse'
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    try:
        payload = {'docs' : json.load (data)}
    except Exception as e:
        response = {'status': u'error', 'code': 400, 'msg': {'reason': str(e)}}
        return json.dumps (response, indent=2)

    for task in payload['docs']:
        task['type'] = 'task'
        task['slug'] = slugify (task['title'])
        task['_id'] = str(uuid.uuid4())

    print payload

    db.post ('_bulk_docs', data=payload)
    return json.dumps (db.status(), indent=2) 

@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def remove (name=None):
    "suppression de tâches"
    pass

@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def search (name=None):
    "recherche de tâches"
    pass
