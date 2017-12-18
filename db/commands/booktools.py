# -*- coding: utf-8 -*-
from flask import current_app
from commands import livres 

import requests, json, uuid, random
from faker import Faker, providers
from slugify import slugify
from prettytable import PrettyTable

from util import util


proxies = {
        'http': 'http://135.245.192.7:8000',
        'https': 'http://135.245.192.7:8000',
        }

# générateur pseudo-aléatoire de catégories
class GenreProvider (providers.BaseProvider):
    def genre (self):
        choix = [u'policier', u'roman', u'théatre', u'poésie']
        return random.choice (choix)

@livres.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre livres')
@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def init (count, name=None):
    u"création de livres exemples"
    config = current_app.config.get_namespace ('COUCHDB_')

    # récupération nom de la base
    db = name if name is not None else config.get ('db')

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

    # génération des livres
    factory = Faker ('fr_FR')
    factory.add_provider (GenreProvider)
    for i in range (0, count):
        title = factory.sentence (nb_words=3)
        payload = {
                "type": "book",
                "title": title,
                "slug": slugify (title),
                "author": factory.last_name(),
                "publisher": factory.word (ext_word_list=('rivages','seuil','etc')),
                "genre": factory.genre(),
                "year":  factory.year(),
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

@livres.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@livres.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre tâches à créer')
@livres.option ('--filter', dest='filter', metavar='filter', default=None, help=u'Filtrage des tâches')
@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, filter, name=None):
    u"liste des livres"
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

    if filter == 'genre':
        target = url + '_design/books/_view/byGenre'
        params ['key']='"policier"'
        params ['reduce'] = False
    else:
        target = url + '_design/books/_view/byId'

    r = requests.get (target, headers=headers, params= params)
    print r.url
    if r.status_code != 200:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    data = []
    table = PrettyTable (['id', 'title', 'genre', 'author', 'year'])

    for item in r.json()['rows']:
        r = requests.get (url + item['id'], headers=headers)

        data.append (
                {
                    'id' : r.json()['_id'],
                    'title': r.json()['title'],
                    'genre': r.json()['genre'],
                    'author': r.json()['author'],
                    'year': r.json()['year']
                }
            )
        table.add_row([r.json()['_id'], r.json()['title'], r.json()['genre'], r.json()['author'], r.json()['year']])

    if f == 'table':
        return table

    sortie = {'total': 10, 'count': 10, 'tasks': data}
    return json.dumps (sortie, indent=2)

@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def add (count, name=None):
    u"ajout d'un livre"
    pass

@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def remove (name=None):
    u"suppression de livres"
    pass

@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def search (name=None):
    u"recherche de livres"
    pass

