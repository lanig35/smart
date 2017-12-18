# -*- coding: utf-8 -*-
import uuid, requests, json
from slugify import slugify

from flask import current_app, request, jsonify, make_response, url_for, abort

from . import bp_api

class InvalidUsage (Exception):
    def __init__ (self, message, status_code, payload=None):
        Exception .__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict (self):
        rv = dict (self.payload or ())
        rv['message'] = self.message
        return rv

@bp_api.errorhandler (InvalidUsage)
def invalid (error):
    response = jsonify (error.to_dict())
    response.status_code = error.status_code
    return response

@bp_api.before_request
def before ():
    print 'before'
    return None

@bp_api.before_request
def version ():
    print 'VERSION'
    return None

@bp_api.route ('/')
def index():
    current_app.logger.info ('request')
    return (u'API!')

@bp_api.route ('/tasks', methods=['GET'])
def tasks ():
    current_app.logger.info ('request')
    return (u'Tasks')

@bp_api.route ('/tasks/<uuid:task_id>', methods=['GET'])
def get_task (task_id):
    current_app.logger.info ('request')
    return (u'Get Task: ' + str(task_id))

@bp_api.route ('/tasks/<int:task_id>', methods=['PUT'])
def modify_task (task_id):
    current_app.logger.info ('request')
    return (u'Modify Task: ' + str(task_id))

@bp_api.route ('/tasks/<uuid:task_id>', methods=['PATCH'])
def patch_task (task_id):
    current_app.logger.info ('request')
    return (u'Patch Task: ' + str(task_id))

@bp_api.route ('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task (task_id):
    current_app.logger.info ('request')
    return (u'Delete Task: ' + str(task_id))

@bp_api.route ('/tasks', methods=['POST'])
def create_task ():
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
    response.headers['Location'] = url_for ('api.get_task', task_id=uuid.uuid4())
    return response 
