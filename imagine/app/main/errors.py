# -*- coding: utf-8 -*-

from flask import request, jsonify

from . import bp_main

@bp_main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response

    return ('404.html'), 404
