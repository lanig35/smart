# -*- coding: utf-8 -*-

from flask import jsonify

from . import bp_api

@bp_api.errorhandler (404)
def not_found (e):
    return jsonify ({'error': 'not found'}), 404
@bp_api.errorhandler (405)
def not_found (e):
    return jsonify ({'error': 'not allowed'}), 405
