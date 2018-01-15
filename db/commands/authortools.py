# -*- coding: utf-8 -*-
from flask import current_app
from commands import auteurs 

import requests, json, uuid, random
from faker import Faker, providers
from slugify import slugify
from prettytable import PrettyTable
import argparse

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
    "création de auteurs exemples"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    # génération des auteurs
    factory = Faker ('fr_FR')
    factory.add_provider (GenreProvider)

    for i in range (0, count):
        name = factory.last_name ()
        first_name = factory.first_name ()
        payload = {
                "type": "auteur",
                "nom": name,
                "prenom": first_name,
                "pays": factory.country()
                }

        if not db.put (str(uuid.uuid4()), data=payload):
            return json.dumps (db.status(), indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': count}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@auteurs.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@auteurs.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre auteurs')
@auteurs.option ('-s', '--start', dest='start', metavar='start', type=int, default=0, help=u'index début')
@auteurs.option ('--filter', dest='filtre', metavar='filter', default=None, help=u'Filtrage des auteurs')
@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, start, filtre, name=None):
    u"liste des auteurs"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    if (start < 0) or (count > 20):
        response = {'status': u'error', 'code': 412, 'msg': {'reason': 'invalid count or start conditions'}}
        return json.dumps (response, indent=2)

    params = {
            'reduce': False,
            'limit': count,
            'skip': start,
            'stale': 'ok'
            }

    if filtre is None:
        target = '_design/authors/_view/parNom'
    else:
        try:
            key,val = filtre.split('=')
        except ValueError as e:
            response = {'status': u'error', 'code': 412, 'msg': {'reason': 'invalid filter format'}}
            return json.dumps (response, indent=2)

        if key not in ('pays','langue','sexe', 'genre'):
            response = {'status': u'error', 'code': 412, 'msg': {'reason': 'invalid filter argument'}}
            return json.dumps (response, indent=2)

        target = '_design/authors/_view/par'+key.capitalize()
#        params ['key']='\"{}\"'.format (val.decode('cp1252').capitalize())
        params ['key']='\"{}\"'.format (val.title())

    # récupération de la liste des documents
    view = db.get (target, params)
    if view is None:
        return json.dumps (db.status(), indent=2)

    # récupération des auteurs
    data = []
    table = PrettyTable (['id', 'Nom', 'Prenom', 'Pays', 'Langue', 'Sexe'])

    total = view['total_rows']
    count = 0
    for author in view['rows']:
        doc = db.get (author['id'])
        count +=1

        data.append (
                {
                    'id' : doc['_id'],
                    'nom': doc['nom'],
                    'prenom': doc['prenom'],
                    'pays': doc['pays'],
                    'langue': doc['langue'],
                    'sexe': doc['sexe']
                }
            )
        table.add_row([doc['_id'], doc['nom'], doc['prenom'], doc['pays'], doc['langue'], doc['sexe']])

    if f == 'table':
        return table

    sortie = {'total': total, 'count': count, 'start': start, 'auteurs': data}
    with open ('alain.json', 'w') as f:
        json.dump (sortie, f)
        import sys
        json.dump (sortie, sys.stdout)
    return json.dumps (sortie, ensure_ascii=False).encode('utf8')

@auteurs.option ('-d', '--db', dest='name', default=None, help=u'Nom de la base')
@auteurs.option ('-c', '--country', dest='country', required=True, help=u'pays')
@auteurs.option ('auteur', nargs=argparse.REMAINDER, help='prénom et nom')
def add (name, country, auteur):
    u"ajout d'un auteur"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    print unicode (country)

    payload = {
            "type": "author",
            "name": auteur[1].capitalize(),
            "firstname": auteur[0].capitalize(),
            "country": country.title()
            }

    print payload
    return

    # verification si auteur existe
    params = {'key': '\"{}\"'.format(payload['name'])}
    view = db.get ('_design/authors/_view/byName', params=params)
    if view is None:
        return json.dumps (db.status(), indent=2)

    if view['rows']:
        response = {'status': u'error', 'code': 412, 'msg': {'reason': 'author already exist', 'name': payload['name']}}
        return json.dumps (response, indent=2)

    key = str(uuid.uuid4())
    if not db.put (key, data=payload):
        return json.dumps (db.status(), indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': u'created', 'id': key}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@auteurs.option ('-i', '--input', dest='data', type=argparse.FileType ('r'), required=True, help=u'fichier de donneés')
@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
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

    for author in payload['docs']:
        author['type'] = 'auteur'
        author['_id'] = str(uuid.uuid4())
        author['pays'] = author['pays'].title()
        author['langue'] = author['langue'].capitalize()
        author['nom'] = author['nom'].title()
        author['prenom'] = author['prenom'].title()
        author['slug'] = slugify (author['prenom']+' '+author['nom'], separator='_')

    db.post ('_bulk_docs', data=payload)
    return json.dumps (db.status(), indent=2)

@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def remove (name=None):
    u"suppression de auteurs"
    pass

@auteurs.option (dest='name', nargs='?', help=u'Nom de la base')
def search (name=None):
    u"recherche de auteurs"
    pass

