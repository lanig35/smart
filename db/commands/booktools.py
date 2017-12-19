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
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

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

        if not db.put (str(uuid.uuid4()), data=payload):
            return json.dumps (db.status(), indent=2)
        
    response = {'status': 'ok', 'code': 200, 'msg': {'result': count}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)
    return 'ok'

@livres.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@livres.option ('-c', '--count', dest='count', metavar='#', type=int, default=5, help=u'Nombre tâches à créer')
@livres.option ('--filter', dest='filter', metavar='filter', default=None, help=u'Filtrage des tâches')
@livres.option (dest='name', nargs='?', help=u'Nom de la base')
def list (f, count, filter, name=None):
    u"liste des livres"
    db = util.Couchdb (name)
    if not db.valid ():
        return json.dumps (db.status(), indent=2)

    # récupération des documents
    params = {
            'limit': count,
            'skip': 0
            }

    if filter == 'genre':
        target = '_design/books/_view/byGenre'
        params ['key']='"policier"'
        params ['reduce'] = False
    else:
        target = '_design/books/_view/byId'

    view = db.get (target, params)
    if view is None:
        return json.dumps (db.status(), indent=2)

    data = []
    table = PrettyTable (['id', 'title', 'genre', 'author', 'year'])

    for book in view['rows']:
        doc = db.get (book['id'])

        data.append (
                {
                    'id' : doc['_id'],
                    'title': doc['title'],
                    'genre': doc['genre'],
                    'author': doc['author'],
                    'year': doc['year']
                }
            )
        table.add_row([doc['_id'], doc['title'], doc['genre'], doc['author'], doc['year']])

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

