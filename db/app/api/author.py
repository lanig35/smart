# -*- coding: utf-8 -*-
import uuid, requests, json
from slugify import slugify

from flask import current_app, request, jsonify, make_response, url_for, abort

from . import bp_api

@bp_api.route ('/authors', methods=['GET'])
def authors ():
    current_app.logger.info ('request')
    r = requests.get ('http://localhost:5984/alain/_all_docs', params={'limit':5, 'include_docs': True})
    response = make_response (jsonify(r.json()), 201)
    return response

@bp_api.route ('/authors/<uuid:author_id>', methods=['GET'])
def get_author (author_id):
    current_app.logger.info ('request')
    r = requests.get ('http://localhost:5984/alain/'+str(author_id))
    return jsonify(r.json())
#    return (u'Get Author: ' + str(author_id))

@bp_api.route ('/authors/<uuid:author_id>', methods=['PUT'])
def modify_author (author_id):
    current_app.logger.info ('request')
    return (u'Modify Author: ' + str(author_id))

@bp_api.route ('/authors/<uuid:author_id>', methods=['PATCH'])
def patch_author (author_id):
    current_app.logger.info ('request')
    return (u'Patch Author: ' + str(author_id))

@bp_api.route ('/authors/<uuid:author_id>', methods=['DELETE'])
def delete_author (author_id):
    current_app.logger.info ('request')
    return (u'Delete Author: ' + str(author_id))

@bp_api.route ('/authors', methods=['POST'])
def create_author ():
    current_app.logger.info ('request')
    body = request.get_json(silent=True)
    if body is None:
        abort (404)
    print body
    payload = {
            "title": body.get('title') or abort (404),
            "slug": slugify(body['title']),
            "category": body.get('category') or u'default',
            "priority": body.get('priority') or u'medium',
            "status": body.get ('status') or u'new'
            }
    if payload['priority'] not in ('low', 'medium', 'high'):
        abort (404)
    if payload['status'] not in ('new', 'done', 'canceled', 'ongoing'):
        raise InvalidUsage ('status not valid', 410, {'status':payload['status'], 'msg': 'error'})
    print payload
    print json.dumps (payload)
    headers = {'Content-type': 'application/json'}
    url = 'http://127.0.0.1:5984/alain/'+str(uuid.uuid4())
    r = requests.put (url, headers=headers, data=json.dumps (payload))
    print r.text
    response = make_response (json.dumps (payload), 201)
    response.headers['Location'] = url_for ('api.get_author', author_id=uuid.uuid4())
    return response 
