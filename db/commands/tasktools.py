# -*- coding: utf-8 -*-
from flask import current_app
from commands import taches

import requests, json, uuid, random
from faker import Faker, providers
from slugify import slugify
from prettytable import PrettyTable

from util import util

# générateur pseudo-aléatoire de statut
class StatusProvider (providers.BaseProvider):
    def status (self):
        status = [u'new', u'done', u'canceled', u'ongoing']
        return random.choice (status)

@taches.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre tâches à créer')
@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def init (count, name=None):
    u"création de tâches exemples"
    config = current_app.config.get_namespace ('COUCHDB_')
    
    # récupération nom de la base
    db = name if name is not None else config.get ('task_db')

    if db is None:
        response = {'status': 'error', 'code': 400, 'msg': {'error': u'bad request', 'reason': u'missing DB name'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # préparation requête
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    url = config.get('url') + db + '/'

    r = requests.head (url, headers=headers)
    if r.status_code != 200:
        response = {'status': 'error', 'code': 404, 'msg': {'error': u'not found', 'reason': 'database does not exist'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # génération des tâches
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
        doc = url + str (uuid.uuid4())
        r = requests.put (doc, headers=headers, data=json.dumps(payload))
        if r.status_code != 201 and r.status_code != 202:
            response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
            current_app.config['logger'].error (response)
            return json.dumps (response, indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': count, 'name': db}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@taches.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@taches.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre tâches à créer')
@taches.option ('--filter', dest='filter', metavar='filter', default=None, help=u'Filtrage des tâches')
@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, filter, name=None):
    u"liste les tâches"
    print filter

    config = current_app.config.get_namespace ('COUCHDB_')
    
    # récupération nom de la base
    db = name if name is not None else config.get ('task_db')

    if db is None:
        response = {'status': 'error', 'code': 400, 'msg': {'error': u'bad request', 'reason': u'missing DB name'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # préparation requête
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    url = config.get('url') + db + '/'

    r = requests.head (url, headers=headers)
    if r.status_code != 200:
        response = {'status': 'error', 'code': 404, 'msg': {'error': u'not found', 'reason': 'database does not exist'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # récupération des documents
    params = {
            'limit': count,
            'skip': 0
            }

    if filter == 'prio':
        target = url + '_design/tasks/_view/byPriority'
        params ['key']='"low"'
        params ['reduce'] = False 
    else:
        target = url + '_design/tasks/_view/byId'

    print target 
    print params

    r = requests.get (target, headers=headers, params= params)
    print r.url
    if r.status_code != 200:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    data = []
    table = PrettyTable (['id', 'title', 'category', 'status', 'priority'])

    for item in r.json()['rows']:
        r = requests.get (url + item['id'], headers=headers)

        data.append (
                {
                    'id' : r.json()['_id'],
                    'title': r.json()['title'],
                    'category': r.json()['category'],
                    'status': r.json()['status'],
                    'priority': r.json()['priority']
                }
            )
        table.add_row([r.json()['_id'], r.json()['title'], r.json()['category'], r.json()['status'], r.json()['priority']])

    if f == 'table':
        return table

    sortie = {'total': 10, 'count': 10, 'tasks': data}
    return json.dumps (sortie, indent=2)

@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def add (count, name=None):
    u"ajout d'une tâche"
    pass

@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def remove (name=None):
    u"suppression de tâches"
    pass

@taches.option (dest='name', nargs='?', help=u'Nom de la base')
def search (name=None):
    u"recherche de tâches"
    pass
