# -*- coding: utf-8 -*-
from flask import current_app
import requests, json

class Couchdb:
    def __init__ (self, name):
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        
        config = current_app.config.get_namespace ('COUCHDB_')

        # récupération nom de la base
        self.db = name if name is not None else config.get ('db')

        if self.db is None:
            self.state = {'status': u'error', 'code': 400, 'msg': {'error': u'bad request', 'reason': u'missing DB name'}}
        else:
            self.url = config.get('url') + self.db + '/'
            # requête couchdb
            r = requests.head (self.url, headers=self.headers)

            if r.status_code != 200:
                self.state = {'status': 'error', 'code': 404, 'db': self.db, 'msg': {'error': u'not found', 'reason': 'database does not exist'}}
            else:
                self.state = {'status': 'ok', 'code': 200, 'db': self.db, 'msg': {'result': u'exists'}}

        if self.state['status'] !='ok':
            current_app.config['logger'].error (self.state)

    def valid (self):
        return (self.state['status'] == 'ok')

    def status (self):
        return self.state

    def get (self, key, params=None):
        r = requests.get (self.url + key, headers=self.headers, params=params)
        if r.status_code != 200:
            self.state = {'status': u'error', 'code': r.status_code, 'msg': r.json()}
            current_app.config['logger'].error (self.state)
            return None

        return r.json() 

    def put (self, key, params=None, data=None):
        r = requests.put (self.url + key, headers=self.headers, params=params, data=json.dumps(data))
        if r.status_code != 201 and r.status_code != 202:
            self.state = {'status': u'error', 'code': r.status_code, 'msg': r.json()}
            current_app.config['logger'].error (self.state)
            return False

        return True

    def post (self, key, params=None, data=None):
        r = requests.post (self.url + key, headers=self.headers, params=params, data=json.dumps(data))
        if r.status_code != 201: 
            self.state = {'status': u'error', 'code': r.status_code, 'msg': r.json()}
            current_app.config['logger'].error (self.state)
            return False

        self.state = {'status': 'ok', 'code': 201, 'msg': {'result': u'created', 'docs': r.json()}}
        return True
        
