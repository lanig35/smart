# -*- coding: utf-8 -*-
from flask import current_app
from commands import auteurs 

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

@auteurs.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre auteurs')
@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def init (count, name=None):
    u"création de auteurs exemples"
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

    # génération des auteurs
    factory = Faker ('fr_FR')
    factory.add_provider (GenreProvider)
    for i in range (0, count):
        name = factory.last_name ()
        first_name = factory.first_name ()
        payload = {
                "type": "author",
                "name": name,
                "firstname": first_name,
                "country": factory.country()
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

@auteurs.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@auteurs.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre auteurs')
@auteurs.option ('--filter', dest='filter', metavar='filter', default=None, help=u'Filtrage des auteurs')
@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, filter, name=None ):
    u"liste des auteurs"
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

    # récupération des documents
    params = {
            'limit': count,
            'skip': 0
            }

    if filter == 'country':
        target = url + '_design/authors/_view/byCountry'
        params ['key']='"Thailande"'
        params ['reduce'] = False
    else:
        target = url + '_design/authors/_view/byId'

    r = requests.get (target, headers=headers, params= params)
    if r.status_code != 200:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    data = []
    table = PrettyTable (['id', 'Name', 'Country'])

    for item in r.json()['rows']:
        r = requests.get (url + item['id'], headers=headers)
        data.append (
                {
                    'id' : r.json()['_id'],
                    'name': r.json()['name'],
                    'country': r.json()['country'],
                }
            )
        table.add_row([r.json()['_id'], r.json()['name'], r.json()['country']])

    if f == 'table':
        return table

    sortie = {'total': 10, 'count': 10, 'authors': data}
    return json.dumps (sortie, indent=2)

    pass

@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def add (count, name=None):
    u"ajout d'un auteur"
    pass

@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def remove (name=None):
    u"suppression de auteurs"
    pass

@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def search (name=None):
    u"recherche de auteurs"
    pass

