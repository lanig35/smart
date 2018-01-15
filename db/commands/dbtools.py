# -*- coding: utf-8 -*-
from flask import current_app
from commands import bases 

import requests, json
from prettytable import PrettyTable
from datetime import datetime

from util import util

@bases.command
def info ():
    u"Statistiques serveur CouchDB"
    r = requests.get ('http://127.0.0.1:5986/_stats')
    return r.json()

@bases.option (dest='name', nargs='?', help=u'Nom de la base')
def creer (name=None):
    u"création de base"
    config = current_app.config.get_namespace('COUCHDB_')

    # récupération nom de la base
    db = name if name is not None else config.get ('db')

    if db is None:
        response = {'status': 'error', 'code': 400, 'msg': {'error': u'bad request', 'reason': u'missing DB name'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # préparation requête
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    auth = (config.get('admin'), config.get ('pass'))
    url = config.get('url') + db 

    # création de la base
    r = requests.put (url, headers=headers, auth=auth)
    if r.status_code != 201:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # installation des design document
    with open ('./tasks.json') as f:
        data = json.load (f)

    r = requests.put (url+'/_design/tasks', headers=headers, auth=auth, data=json.dumps(data))
    if r.status_code != 201:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        # remove the database
        requests.delete (url, headers=headers, auth=auth)
        return json.dumps (response, indent=2)

    with open ('./books.json') as f:
        data = json.load (f)

    r = requests.put (url+'/_design/books', headers=headers, auth=auth, data=json.dumps(data))
    if r.status_code != 201:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        # remove the database
        requests.delete (url, headers=headers, auth=auth)
        return json.dumps (response, indent=2)

    with open ('./authors.json') as f:
        data = json.load (f)

    r = requests.put (url+'/_design/authors', headers=headers, auth=auth, data=json.dumps(data))
    if r.status_code != 201:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        # remove the database
        requests.delete (url, headers=headers, auth=auth)
        return json.dumps (response, indent=2)
    response = {'status': 'ok', 'code': 201, 'msg': {'result': 'created', 'name': db}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)

@bases.option (dest='name', nargs='?', help=u'Database name')
def supprimer (name=None):
    u"Suppression base"
    config = current_app.config.get_namespace ('COUCHDB_')
    
    # récupération nom de la base
    db = name if name is not None else config.get ('db')

    if db is None:
        response = {'status': 'error', 'code': 400, 'msg': {'error': u'bad request', 'reason': u'missing DB name'}}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    # préparation requête
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    auth = (config.get('admin'), config.get ('pass'))
    url = config.get('url') + db

    # suppression base
    r = requests.delete (url, headers=headers, auth=auth)
    if r.status_code != 200:
        response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
        current_app.config['logger'].error (response)
        return json.dumps (response, indent=2)

    response = {'status': 'ok', 'code': 200, 'msg': {'result': u'deleted', 'name': db}}
    current_app.config['logger'].info (response)
    return json.dumps (response, indent=2)


@bases.option ('-f', '--format', dest='f', choices=['json','table'], default='json', help=u'format de sortie')
@bases.option (dest='name', nargs='?', help=u'nom de la base')
def lister (f, name=None):
    u"info base"
    config = current_app.config.get_namespace ('COUCHDB_')
    
    # récupération nom de la base
    db = name if name is not None else config.get ('db')

    # préparation requête
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    base = []
    if db is None:
        url = config.get('url') + '_all_dbs'
        r = requests.get (url, headers=headers)

        if r.status_code != 200:
            response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
            current_app.config['logger'].error (response)
            return json.dumps (response, indent=2)
        
        base = r.json()
    else:
        base.append(db)

    info = []
    for item in base:
        if not item.startswith ('_'):
            url = config.get('url') + item 

            # récupération des infos
            r = requests.get (url, headers=headers)
            if r.status_code != 200:
                response = {'status': 'error', 'code': r.status_code, 'msg': r.json()}
                current_app.config['logger'].error (response)
                return json.dumps (response, indent=2)

            current_app.config['logger'].info (item)

            data = r.json()
            db = {}
            db ['nom'] = data['db_name']
            db ['docs'] = data['doc_count']
            db ['suppr'] = data['doc_del_count']
            db ['taille'] = data['data_size']
            db ['disque'] = data['disk_size']

            info.append (db)

    if f == 'json':
      return json.dumps (info, indent=2)

    table = PrettyTable (['nom', 'docs', 'suppr', 'taille', 'disque'])
    for db in info:
        table.add_row ([db['nom'], db['docs'], db['suppr'], db['taille'], db['disque']])
    return table

